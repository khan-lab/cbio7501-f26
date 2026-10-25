"""Download the LTEE example data and check that it is exactly what we expect.

Reads   metadata/sources.tsv        where each file comes from, provider md5
Checks  metadata/checksums.sha256   sha256 of every raw file we keep
Writes  data/raw/fastq/*.fastq and data/raw/reference/ecoli_rel606.fasta.gz,
        then makes them read-only (raw data is never edited).

Run it again at any time: files that are already present and correct are
not downloaded again. Use --verify-only to check without downloading.
Works on Linux, macOS and Windows (only the Python standard library).
"""

import argparse
import csv
import hashlib
import http.client
import os
import shutil
import stat
import sys
import tarfile
import tempfile
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / "metadata" / "sources.tsv"
CHECKSUMS = ROOT / "metadata" / "checksums.sha256"


def digest(path, algorithm):
    h = hashlib.new(algorithm)
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def expected_sha256():
    expected = {}
    for line in CHECKSUMS.read_text().splitlines():
        if line.strip():
            value, name = line.split(maxsplit=1)
            expected[name.strip().lstrip("*")] = value
    return expected


def verify(expected):
    """Return the files that are missing or have the wrong checksum."""
    bad = []
    for name, value in expected.items():
        path = ROOT / name
        if not path.exists():
            bad.append((name, "missing"))
        elif digest(path, "sha256") != value:
            bad.append((name, "checksum differs"))
    return bad


def download(url, dest, attempts=3):
    print(f"  downloading {url}", flush=True)
    request = urllib.request.Request(url, headers={"User-Agent": "curl/8 (cbio7501 ltee-project)"})
    for attempt in range(1, attempts + 1):
        try:
            # timeout: give up if the server sends nothing for 60 s
            with urllib.request.urlopen(request, timeout=60) as response, open(dest, "wb") as out:
                total = int(response.headers.get("Content-Length") or 0)
                done, shown = 0, -1
                while chunk := response.read(1 << 20):
                    out.write(chunk)
                    done += len(chunk)
                    if total and done * 10 // total > shown:  # progress every 10%
                        shown = done * 10 // total
                        print(f"  {done / 1e6:.0f} of {total / 1e6:.0f} MB", flush=True)
            return
        except (OSError, http.client.HTTPException) as err:  # network hiccup: wait and try again
            if attempt == attempts:
                raise
            print(f"  attempt {attempt} failed ({err}); retrying in {5 * attempt} s")
            time.sleep(5 * attempt)


def fetch(source, tmp):
    archive = Path(tmp) / source["name"]
    download(source["url"], archive)
    md5 = digest(archive, "md5")
    if md5 != source["md5"]:
        sys.exit(f"ERROR {source['name']}: md5 {md5} does not match the provider's {source['md5']}")
    print(f"  md5 matches the provider ({md5})", flush=True)
    dest = ROOT / source["dest"]
    if source["unpack"] == "tar":
        dest.mkdir(parents=True, exist_ok=True)
        with tarfile.open(archive) as tar:
            for member in tar.getmembers():
                if member.isfile():
                    member.name = Path(member.name).name  # drop the sub/ folder
                    tar.extract(member, dest, filter="data")
    else:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(archive, dest)


def make_read_only(expected):
    for name in expected:
        path = ROOT / name
        mode = path.stat().st_mode
        os.chmod(path, mode & ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-only", action="store_true", help="only check the files")
    args = parser.parse_args()

    expected = expected_sha256()
    bad = verify(expected)
    if bad and not args.verify_only:
        with open(SOURCES, newline="") as fh:
            sources = list(csv.DictReader(fh, delimiter="\t"))
        # temporary files go inside the project, on the same disk as the data
        with tempfile.TemporaryDirectory(dir=ROOT / "data") as tmp:
            for source in sources:
                targets = [n for n, _ in bad if n.startswith(source["dest"])]
                if targets:
                    print(f"{source['name']}: {len(targets)} file(s) to fetch", flush=True)
                    for name in expected:  # remove read-only leftovers from this source
                        path = ROOT / name
                        if name.startswith(source["dest"]) and path.exists():
                            os.chmod(path, stat.S_IWUSR | stat.S_IRUSR)
                            path.unlink()
                    fetch(source, tmp)
        bad = verify(expected)

    for name, problem in bad:
        print(f"FAILED {name}: {problem}")
    if bad:
        sys.exit(f"{len(bad)} of {len(expected)} raw files are missing or changed")
    make_read_only(expected)
    print(f"OK: all {len(expected)} raw files present, sha256 verified, read-only")


if __name__ == "__main__":
    main()
