"""Check a project (a capstone, or a student's ltee-project) for the items of
the rubric that a program can check. It does not grade: it lists evidence
for the grader.

Usage (from the course repository):
    pixi run check-capstone path/to/clone-of-student-project

Run it on a fresh clone. Items it cannot judge (quality of the report, of the
README text, of the history) are left to the grader and the reproduce report.
"""

import re
import subprocess
import sys
import tomllib
from pathlib import Path

import yaml


def tasks_in(manifest):
    names = set(manifest.get("tasks", {}))
    for feature in manifest.get("feature", {}).values():
        names |= set(feature.get("tasks", {}))
    return names


def git_files(root):
    try:
        out = subprocess.run(["git", "-C", str(root), "ls-files"], capture_output=True, text=True, check=True)
        return out.stdout.splitlines()
    except (OSError, subprocess.CalledProcessError):
        return None


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    root = Path(sys.argv[1]).resolve()
    checks = []

    def check(area, ok, item, evidence=""):
        checks.append((area, "yes" if ok else "NO", item, evidence))

    # Reproducibility and environment
    manifest_path = root / "pixi.toml"
    manifest = tomllib.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    check("Environment", manifest_path.exists(), "pixi.toml present")
    check("Environment", (root / "pixi.lock").exists(), "pixi.lock committed next to pixi.toml")
    tasks = tasks_in(manifest)
    check("Automation", "reproduce" in tasks, "a `reproduce` task", ", ".join(sorted(tasks)))
    workflows = list((root / ".github" / "workflows").glob("*.y*ml"))
    ci = [w.name for w in workflows if "pixi run reproduce" in w.read_text()]
    check("Reproduce", bool(ci), "CI workflow runs `pixi run reproduce`", ", ".join(ci))
    engines = [p for p in ("workflow/Snakefile", "workflow/nextflow/main.nf", "Snakefile", "main.nf") if (root / p).exists()]
    check("Automation", bool(engines) or len(tasks) > 3, "workflow file or several Pixi tasks", ", ".join(engines))

    # Data management
    gitignore = (root / ".gitignore").read_text() if (root / ".gitignore").exists() else ""
    check("Data", "data/raw" in gitignore, "raw data ignored by Git")
    check("Data", ".pixi" in gitignore, "environments ignored by Git")
    sums = [p.name for p in (root / "metadata").glob("*") if re.search(r"(sha256|md5|checksum)", p.name)]
    check("Data", bool(sums), "checksums of raw data in metadata/", ", ".join(sums))
    tracked = git_files(root)
    if tracked is not None:
        raw = [f for f in tracked if f.startswith("data/raw/") and not f.endswith("README.md")]
        check("Data", not raw, "no raw data committed", ", ".join(raw[:5]))
        big = [f for f in tracked if (root / f).is_file() and (root / f).stat().st_size > 10_000_000]
        check("Version control", not big, "no files over 10 MB in Git", ", ".join(big[:5]))

    # Literate programming
    reports = [p.name for p in (root / "reports").glob("*.qmd")] if (root / "reports").exists() else []
    check("Report", bool(reports), "Quarto report source in reports/", ", ".join(reports))

    # Documentation and openness
    readme = (root / "README.md").read_text().lower() if (root / "README.md").exists() else ""
    for word, item in [("reproduc", "README: how to reproduce"), ("hardware", "README: hardware"),
                       ("output", "README: expected outputs"), ("data", "README: data source"),
                       ("cite", "README: how to cite"), ("license", "README: license")]:
        check("Documentation", word in readme, item)
    check("Openness", (root / "LICENSE").exists() or (root / "LICENSE.md").exists(), "LICENSE file")
    cff_path = root / "CITATION.cff"
    cff_ok, cff_note = False, "missing"
    if cff_path.exists():
        try:
            cff = yaml.safe_load(cff_path.read_text())
            missing = [k for k in ("cff-version", "message", "title", "authors") if k not in cff]
            cff_ok, cff_note = not missing, ("missing " + ", ".join(missing)) if missing else "required keys present"
        except yaml.YAMLError as err:
            cff_note = f"not valid YAML: {err}"
    check("Openness", cff_ok, "CITATION.cff (validate fully with `pixi exec cffconvert --validate`)", cff_note)
    # Only a Zenodo DOI counts: the README also cites papers and data by DOI.
    # Required for the ltee-project; optional for a capstone, where a sandbox
    # DOI (10.5072) is fine.
    release_dois = sorted(set(re.findall(r"10\.5281/zenodo\.\d+", readme)))
    sandbox_dois = sorted(set(re.findall(r"10\.5072/zenodo\.\d+", readme)))
    evidence = ", ".join(release_dois + [d + " (sandbox)" for d in sandbox_dois])
    check("Openness", bool(release_dois or sandbox_dois),
          "release DOI in README (ltee-project: Zenodo; capstone: optional, sandbox fine)", evidence)

    width = max(len(c[2]) for c in checks)
    print(f"Project checks for {root}\n")
    for area, ok, item, evidence in checks:
        print(f"{ok:4s} {area:16s} {item:<{width}}  {evidence}")
    passed = sum(1 for c in checks if c[1] == "yes")
    print(f"\n{passed} of {len(checks)} automatic checks pass. Also needed: the green Reproduce check on GitHub "
          "and the partner's reproduce report.")


if __name__ == "__main__":
    main()
