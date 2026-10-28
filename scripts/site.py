"""Build or preview the website with the profile that event.yml asks for.

The `format:` in event.yml picks a Quarto profile (_quarto-<profile>.yml),
which adds that format's menu items. Through Pixi:

    pixi run render                      # python scripts/site.py render
    pixi run preview                     # python scripts/site.py preview
    pixi run render pages/05-pixi.qmd    # extra arguments go to Quarto
"""
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
# format in event.yml -> Quarto profile (keep in step with
# assets/filters/event-check.lua)
PROFILES = {
    "course-7week": "course",
    "workshop-4day": "workshop",
    "workshop-5day": "workshop",
    "self-paced": "self-paced",
}


def profile() -> str:
    event = yaml.safe_load((ROOT / "event.yml").read_text(encoding="utf-8"))["event"]
    fmt = event.get("format")
    if fmt not in PROFILES:
        sys.exit(f"event.yml: format must be one of {', '.join(PROFILES)}, not {fmt!r}")
    return PROFILES[fmt]


def main() -> int:
    if len(sys.argv) < 2 or sys.argv[1] not in ("render", "preview"):
        sys.exit("usage: python scripts/site.py render|preview [quarto arguments]")
    prof = profile()
    print(f"event.yml: building with the {prof} profile", flush=True)
    quarto = shutil.which("quarto") or "quarto"
    return subprocess.call([quarto, *sys.argv[1:], "--profile", prof], cwd=ROOT)


if __name__ == "__main__":
    sys.exit(main())
