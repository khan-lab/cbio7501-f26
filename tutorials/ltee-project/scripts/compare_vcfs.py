"""Compare the final variant calls of two runs of the pipeline.

Usage: python scripts/compare_vcfs.py results/vcf results/nextflow/vcf

Header lines (starting with #) record dates, commands and tool versions, so
they always differ between runs. This script compares only the variant
records. It prints one line per sample and exits with 1 if any sample
differs, so it can be used as a test.
"""

import sys
from pathlib import Path


def records(path):
    with open(path) as fh:
        return [line.rstrip("\n") for line in fh if not line.startswith("#")]


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    first, second = Path(sys.argv[1]), Path(sys.argv[2])
    names = sorted(p.name for p in first.glob("*_final_variants.vcf"))
    if not names:
        sys.exit(f"no *_final_variants.vcf files in {first}")
    differ = 0
    for name in names:
        other = second / name
        if not other.exists():
            print(f"{name}: missing in {second}")
            differ += 1
            continue
        a, b = records(first / name), records(other)
        if a == b:
            print(f"{name}: identical ({len(a)} variants)")
        else:
            only_a, only_b = len(set(a) - set(b)), len(set(b) - set(a))
            print(f"{name}: DIFFERENT ({len(a)} vs {len(b)} variants; {only_a} only in first, {only_b} only in second)")
            differ += 1
    sys.exit(1 if differ else 0)


if __name__ == "__main__":
    main()
