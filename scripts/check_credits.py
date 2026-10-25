"""Check that every adapted source is credited.

Rules (see CONTRIBUTING.md and pages/credits.qmd):

1. Every lesson page (pages/*.qmd) and deck (lectures/*/*.qmd) must have an
   `adapted_from:` key in its front matter. Use `adapted_from: []` for
   material that is entirely our own, so the choice is explicit.
2. Every adapted_from entry needs `title`, `url`, `license` and `accessed`,
   and its `url` must appear on pages/credits.qmd.
3. Licenses we cannot adapt (non-commercial, share-alike, unknown) are not
   allowed in adapted_from: those sources are linked, not adapted.

Exit code 0 when all checks pass, 1 otherwise.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CREDITS = ROOT / "pages" / "credits.qmd"
REQUIRED = ("title", "url", "license", "accessed")
ADAPTABLE = ("CC BY 4.0", "CC0", "MIT", "BSD-3-Clause", "BSD", "Own work")
SKIP = {"credits.qmd"}


def front_matter(path: Path) -> dict | None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    return yaml.safe_load(text[3:end]) or {}


def main() -> int:
    credits_text = CREDITS.read_text(encoding="utf-8")
    files = sorted((ROOT / "pages").glob("*.qmd")) + sorted((ROOT / "lectures").glob("*/*.qmd"))
    errors: list[str] = []
    checked = 0
    for path in files:
        if path.name in SKIP:
            continue
        rel = path.relative_to(ROOT)
        meta = front_matter(path)
        if meta is None:
            errors.append(f"{rel}: no YAML front matter")
            continue
        if "adapted_from" not in meta:
            errors.append(f"{rel}: missing `adapted_from:` (use `adapted_from: []` for own material)")
            continue
        for i, entry in enumerate(meta["adapted_from"] or []):
            checked += 1
            where = f"{rel}: adapted_from[{i}]"
            missing = [k for k in REQUIRED if not entry.get(k)]
            if missing:
                errors.append(f"{where}: missing {', '.join(missing)}")
                continue
            if not any(entry["license"].startswith(ok) for ok in ADAPTABLE):
                errors.append(f"{where}: license {entry['license']!r} cannot be adapted; link it instead")
            if entry["url"] not in credits_text:
                errors.append(f"{where}: {entry['url']} is not listed on pages/credits.qmd")
    for e in errors:
        print(f"ERROR {e}")
    print(f"check_credits: {len(files) - len(SKIP)} files, {checked} adapted_from entries, {len(errors)} errors")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
