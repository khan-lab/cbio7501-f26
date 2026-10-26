"""Run the code blocks of the tutorials, in order, in a clean folder.

The tutorials are the test: every shell block a learner is asked to run is
marked in the .qmd source, and this script runs exactly those blocks.

Code block classes (Quarto ignores the extra classes when rendering):

  ```{.bash .run}                 run it (bash, Linux or macOS)
  ```{.bash .run-ci}              run it only with --ci (git writes, Docker)
  ```{.bash .expect-fail}         run it and require a non-zero exit (Break it)
  ```{.bash .run-ci .expect-fail} both: only with --ci, and must fail
  ```{.python filename="x.py" .write}   write the block to that file
  ```{.toml filename="x" .append}       append the block to that file
  ```{.bash .norun}               show only (interactive, long, or optional)

In .write and .append blocks, a cell fence written as ```{{python}} (the form
Quarto needs to display a cell without running it) is saved as ```{python}.

Shell blocks (bash, sh, zsh) with none of these classes are reported as
"unmarked" and fail the run, so every command is either tested or explicitly
skipped. PowerShell blocks are never run here (no Windows runner locally) and
are counted as untested.

A page can declare in its front matter which pages must run first (they build
the project state it starts from):

  test:
    needs: [02-project-organization]
    timeout: 3600

Usage:
  python scripts/test_tutorials.py                       # all tested pages, one combined run
  python scripts/test_tutorials.py 02-project-organization 07-quarto
  python scripts/test_tutorials.py --list                # show block counts
  python scripts/test_tutorials.py --ci                  # also run .run-ci blocks
  python scripts/test_tutorials.py --workdir DIR         # where runs happen

Unpublished URLs (for example the template inside this repo before it is on
GitHub) are swapped for local paths using tests/substitutions.yml.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
PAGES = ROOT / "pages"
SUBSTITUTIONS = ROOT / "tests" / "substitutions.yml"
SHELLS = {"bash", "sh", "zsh", "shell", "console"}
MARKERS = {"run", "run-ci", "expect-fail", "write", "append", "norun"}
FENCE = re.compile(r"^(?P<indent>[ \t]*)(?P<fence>`{3,}|~{3,})\s*(?P<info>.*)$")


@dataclass
class Block:
    page: str
    line: int
    lang: str
    classes: list[str]
    attrs: dict[str, str]
    code: str

    @property
    def marker(self) -> str | None:
        found = [c for c in self.classes if c in MARKERS]
        return found[0] if found else None


@dataclass
class Page:
    stem: str
    path: Path
    meta: dict
    blocks: list[Block] = field(default_factory=list)

    @property
    def needs(self) -> list[str]:
        return list((self.meta.get("test") or {}).get("needs") or [])

    @property
    def timeout(self) -> int:
        return int((self.meta.get("test") or {}).get("timeout") or 3600)

    @property
    def tested(self) -> bool:
        return any(b.marker in {"run", "run-ci", "expect-fail", "write", "append"} for b in self.blocks)


def parse_info(info: str) -> tuple[str, list[str], dict[str, str]]:
    info = info.strip()
    if not info:
        return "", [], {}
    if not info.startswith("{"):
        return info.split()[0], [], {}
    inner = info.strip("{}").strip()
    attrs = dict(re.findall(r'([\w-]+)="([^"]*)"', inner))
    inner = re.sub(r'[\w-]+="[^"]*"', "", inner)
    classes = [t[1:] for t in inner.split() if t.startswith(".")]
    lang = classes[0] if classes else ""
    return lang, classes[1:] if classes else [], attrs


def parse_page(path: Path) -> Page:
    text = path.read_text(encoding="utf-8")
    meta = {}
    if text.startswith("---"):
        end = text.find("\n---", 3)
        meta = yaml.safe_load(text[3:end]) or {}
    lines = text.splitlines()
    page = Page(path.stem, path, meta)
    i = 0
    while i < len(lines):
        m = FENCE.match(lines[i])
        if not m:
            i += 1
            continue
        fence, indent = m.group("fence"), len(m.group("indent"))
        lang, classes, attrs = parse_info(m.group("info"))
        start = i
        body = []
        i += 1
        while i < len(lines):
            close = re.match(r"^[ \t]*(`{3,}|~{3,})\s*$", lines[i])
            if close and close.group(1)[0] == fence[0] and len(close.group(1)) >= len(fence):
                break
            body.append(lines[i][indent:] if lines[i][:indent].strip() == "" else lines[i])
            i += 1
        i += 1
        page.blocks.append(Block(page.stem, start + 1, lang, classes, attrs, "\n".join(body)))
    return page


def load_pages() -> dict[str, Page]:
    return {p.stem: parse_page(p) for p in sorted(PAGES.glob("*.qmd"))}


def substitutions() -> dict[str, str]:
    if not SUBSTITUTIONS.exists():
        return {}
    raw = yaml.safe_load(SUBSTITUTIONS.read_text()) or {}
    return {k: str(v).replace("{ROOT}", str(ROOT)) for k, v in raw.items()}


CELL_ESCAPE = re.compile(r"^([ \t]*`{3,})\{\{([^{}]+)\}\}", re.M)


def unescape_cells(code: str) -> str:
    """Pages show Quarto cells as ```{{python}} so Quarto does not run them;
    the file a learner saves must contain ```{python}."""
    return CELL_ESCAPE.sub(r"\1{\2}", code)


def heredoc(path: str, code: str, mode: str) -> str:
    code = unescape_cells(code)
    tag = "__CBIO7501_EOF__"
    op = ">>" if mode == "append" else ">"
    d = os.path.dirname(path)
    mk = f"mkdir -p {shlex.quote(d)}\n" if d else ""
    return f"{mk}cat {op} {shlex.quote(path)} <<'{tag}'\n{code}\n{tag}\n"


def script_for(page: Page, ci: bool, subs: dict[str, str]) -> tuple[str, dict]:
    stats = {"run": 0, "write": 0, "expect-fail": 0, "skipped-ci": 0, "norun": 0, "powershell": 0, "unmarked": []}
    out = [f"\n# ===== {page.stem} =====\n", f"echo '>>> page {page.stem}'\n"]
    for b in page.blocks:
        code = b.code
        for old, new in subs.items():
            code = code.replace(old, new)
        where = f"{page.stem}.qmd:{b.line}"
        mk = b.marker
        if b.lang in {"powershell", "pwsh", "ps1"}:
            stats["powershell"] += 1
            continue
        if mk is None:
            if b.lang in SHELLS:
                stats["unmarked"].append(where)
            continue
        if mk == "norun":
            stats["norun"] += 1
            continue
        if mk == "run-ci" or "run-ci" in b.classes:
            if not ci:
                stats["skipped-ci"] += 1
                continue
            if "expect-fail" in b.classes:  # {.bash .run-ci .expect-fail}
                mk = "expect-fail"
        out.append(f"echo '>>> {where} ({mk})'\n")
        if mk in {"write", "append"}:
            fname = b.attrs.get("filename")
            if not fname:
                raise SystemExit(f"{where}: .{mk} block needs filename=")
            out.append(heredoc(fname, code, mk))
            stats["write"] += 1
        elif mk == "expect-fail":
            out.append(f"if ( set -e\n{code}\n); then echo 'FAIL: {where} was expected to fail but succeeded'; exit 97; fi\n")
            out.append(f"echo '>>> {where} failed as expected'\n")
            stats["expect-fail"] += 1
        else:
            out.append(code + "\n")
            stats["run"] += 1
    return "".join(out), stats


def order(pages: dict[str, Page], wanted: list[str]) -> list[str]:
    seen: list[str] = []

    def visit(stem: str, stack: tuple[str, ...] = ()):
        if stem in stack:
            raise SystemExit(f"dependency cycle: {' -> '.join(stack + (stem,))}")
        if stem in seen:
            return
        if stem not in pages:
            raise SystemExit(f"unknown page {stem}")
        for dep in pages[stem].needs:
            visit(dep, stack + (stem,))
        seen.append(stem)

    for w in wanted:
        visit(w)
    return seen


def pixi_cache_dir() -> str | None:
    """The package cache of the person running the tests, to share downloads."""
    try:
        out = subprocess.run(["pixi", "info", "--json"], capture_output=True, text=True, check=True,
                             env={k: v for k, v in os.environ.items() if not k.startswith("PIXI_PROJECT")})
        return json.loads(out.stdout).get("cache_dir")
    except (OSError, subprocess.CalledProcessError, ValueError):
        return None


def clean_env(workdir: Path) -> dict[str, str]:
    """A learner-like environment: own HOME, no activated environments.

    Each run gets a fresh HOME inside its work folder (so ~/cbio7501 in the
    tutorials is a new, empty folder), but shares the Pixi package cache so
    packages are not downloaded again for every lesson.
    """
    keep = {"PIXI_NO_TELEMETRY", "DO_NOT_TRACK"}
    drop = ("PIXI_", "CONDA", "_CONDA", "INIT_CWD", "VIRTUAL_ENV", "PYTHON", "XDG_", "NXF_", "MPLCONFIGDIR",
            "JAVA_HOME")
    env = {k: v for k, v in os.environ.items() if k in keep or not k.startswith(drop)}
    # Drop the course environment from PATH so the tutorial only sees what a
    # learner has: pixi plus the system tools.
    course_env = str(ROOT / ".pixi")
    env["PATH"] = os.pathsep.join(p for p in env.get("PATH", "").split(os.pathsep) if course_env not in p)
    home = workdir / "home"
    home.mkdir(parents=True, exist_ok=True)
    env["HOME"] = str(home)
    tmp = workdir / "tmp"  # own temp folder: parallel runs must not share one
    tmp.mkdir(parents=True, exist_ok=True)
    env["TMPDIR"] = str(tmp)
    cache = pixi_cache_dir()
    if cache:
        env["PIXI_CACHE_DIR"] = cache
    env["CBIO7501_TEST"] = "1"
    env["CBIO7501_COURSE_DIR"] = str(ROOT)
    return env


def run_one(stem: str, pages: dict[str, Page], args, subs, base: Path, targets: list[str] | None = None) -> dict:
    chain = order(pages, targets or [stem])
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    workdir = base / f"{stem}-{stamp}"
    workdir.mkdir(parents=True)
    parts = ["#!/usr/bin/env bash\n# -e: stop at the first failing command. No pipefail: a learner's shell does not set it,\n# and `cmd | head` must not count as a failure.\nset -e\n"]
    stats = {}
    for s in chain:
        text, st = script_for(pages[s], args.ci, subs)
        parts.append(text)
        stats[s] = st
    script = workdir / "run.sh"
    script.write_text("".join(parts))
    log = workdir / "run.log"
    unmarked = [u for s in chain for u in stats[s]["unmarked"]]
    t0 = time.time()
    if unmarked and not args.allow_unmarked:
        rc, status = 98, "unmarked shell blocks"
    else:
        with log.open("w") as fh:
            try:
                rc = subprocess.run(["bash", str(script)], cwd=workdir, env=clean_env(workdir),
                                    stdout=fh, stderr=subprocess.STDOUT,
                                    timeout=sum(pages[s].timeout for s in chain)).returncode
            except subprocess.TimeoutExpired:
                rc = 124
        status = "pass" if rc == 0 else f"fail (exit {rc})"
    result = {"page": stem, "chain": chain, "status": status, "seconds": round(time.time() - t0, 1),
              "workdir": str(workdir), "stats": stats, "unmarked": unmarked}
    (workdir / "result.json").write_text(json.dumps(result, indent=2))
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pages", nargs="*", help="page stems, e.g. 05-pixi (default: all tested pages)")
    ap.add_argument("--ci", action="store_true", help="also run .run-ci blocks (git writes, Docker)")
    ap.add_argument("--list", action="store_true", help="list block counts and exit")
    ap.add_argument("--workdir", default=os.environ.get("CBIO7501_TEST_WORKDIR"), help="base folder for runs")
    ap.add_argument("--allow-unmarked", action="store_true", help="do not fail on unmarked shell blocks")
    ap.add_argument("--separate", action="store_true",
                    help="with no page names: run every page separately (slow) instead of one combined run")
    args = ap.parse_args()

    pages = load_pages()
    subs = substitutions()
    if args.list:
        for stem, p in pages.items():
            _, st = script_for(p, args.ci, subs)
            print(f"{stem:32s} run={st['run']:3d} write={st['write']:3d} fail={st['expect-fail']:2d} "
                  f"ci={st['skipped-ci']:2d} norun={st['norun']:3d} ps={st['powershell']:2d} "
                  f"unmarked={len(st['unmarked'])} needs={','.join(p.needs) or '-'}")
            for u in st["unmarked"]:
                print(f"    unmarked: {u}")
        return 0

    tested = [s for s, p in pages.items() if p.tested]
    base = Path(args.workdir) if args.workdir else Path(tempfile.mkdtemp(prefix="cbio7501-tests-"))
    base = base.resolve()
    base.mkdir(parents=True, exist_ok=True)
    if args.pages or args.separate:
        # each page in its own folder, with the pages it needs run first
        runs = [(stem, None) for stem in (args.pages or tested)]
    else:
        # all tested pages once, in dependency order, in one folder (the
        # learner's path through the course; much faster than separate runs)
        runs = [("all", tested)]
    results = []
    for stem, targets in runs:
        print(f"--- {stem} ...", flush=True)
        r = run_one(stem, pages, args, subs, base, targets)
        results.append(r)
        print(f"--- {stem}: {r['status']} in {r['seconds']} s (log: {r['workdir']}/run.log)", flush=True)
        for u in r["unmarked"]:
            print(f"    unmarked shell block: {u}")
        log = Path(r["workdir"]) / "run.log"
        if r["status"] != "pass" and log.exists():
            # the end of the log names the failing block (">>> page.qmd:line"),
            # so CI shows it without downloading the logs
            tail = log.read_text(errors="replace").splitlines()[-40:]
            print(f"--- last {len(tail)} lines of the log:", *tail, "--- end of log", sep="\n", flush=True)
    failed = [r for r in results if r["status"] != "pass"]
    (base / "summary.json").write_text(json.dumps(results, indent=2))
    print(f"test_tutorials: {len(results) - len(failed)} passed, {len(failed)} failed; summary in {base}/summary.json")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
