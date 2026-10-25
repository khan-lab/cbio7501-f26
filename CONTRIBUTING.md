# Contributing and maintaining

Thank you for improving the workshop. Issues and pull requests are welcome.

## Build the site

You need [Pixi](https://pixi.prefix.dev/latest/). From the repository folder:

```bash
pixi run render          # build the website into _site/
pixi run preview         # live preview while you edit
pixi run check-credits   # every adapted source is on the credits page
pixi run check-links     # internal links in the rendered site
```

## Repository layout

| Path | Content |
|------|---------|
| `pages/NN-topic.qmd` | tutorials, numbered in teaching order (the credits page maps each to its NBIS source) |
| `lectures/NN-topic/NN-topic.qmd` | slide decks (RevealJS); shared settings in `lectures/_metadata.yml` |
| `quizzes/`, `assessment/` | quiz banks, capstone rubric, reproduce report, checker |
| `cheatsheets/` | one cheat sheet per tool; `_metadata.yml` gives them their table layout |
| `tutorials/ltee-project/` | the finished example project (as after lesson 12) |
| `templates/cookiecutter-repro-project/` | the project template used in lesson 02 |
| `scripts/` | `test_tutorials.py`, `check_credits.py` |
| `assets/filters/adapted-from.lua` | turns `adapted_from:` front matter into attribution |
| `assets/shortcodes/pixi-version.lua` | `{{< pixi-version >}}`: the Pixi version in the footer (Quarto's `{{< version >}}` gives Quarto's) |
| `assets/css/` | the look: `theme-light.scss` and `theme-dark.scss` (color tokens), `styles.scss` (site), `slides.scss` (decks), `fonts.css` |
| `assets/fonts/` | Inter and JetBrains Mono, served from the site (SIL OFL 1.1) |
| `assets/images/` | our figures (`diagrams/`, LTEE screenshots) and third-party CC BY figures (`nbis/`, with a README of sources) |
| `docs/` | build log and build report of the first version |

## Writing a tutorial

Follow the structure of the existing pages: at-a-glance box, overview and
learning outcomes (at "apply" level, each tied to a check), numbered steps
with expected output, *Try it yourself* with folded solutions, a *Break it*
exercise, troubleshooting, *Apply it to your own mini-analysis*, key points,
further reading. Use OS tabs where commands differ.

Lessons, decks and quizzes do not name weeks or weekdays, so they work for the
course, the workshop and self-study alike: give durations in the at-a-glance
box and refer to other lessons by number. When each lesson is taught belongs
in `schedule-course.qmd`, `schedule-workshop.qmd` and `syllabus.qmd` only. The
sidebar in `_quarto.yml` groups lessons by topic.

When a lesson changes a command, change its cheat sheet in `cheatsheets/`
too: the sheets are not run by the tests, and each one links to the lesson
sections it summarizes, so the link check catches renamed sections.

### Every command is a test

`pixi run test-tutorials` runs the tutorials in a fresh folder, in teaching
order, as a learner would. Mark every code block:

| Block | Meaning |
|-------|---------|
| ```` ```{.bash .run} ```` | run it |
| ```` ```{.bash .expect-fail} ```` | run it; it must fail (Break it) |
| ```` ```{.bash .run-ci} ```` | run only with `--ci` (Git writes, Docker): in GitHub Actions |
| ```` ```{.python filename="x.py" .write} ```` | write the block to that file (`.append` appends) |
| ```` ```{.bash .norun} ```` | show only (interactive, needs accounts, destructive) |

Unmarked shell blocks fail the test run, so nothing slips through. An `.expect-fail` block runs in a subshell, so a `cd` inside it does not
carry over: put `cd` in a `.run` block of its own. Declare in
the front matter which lessons must run first (`test: needs: [...]`).
Show Quarto cells inside code blocks as ```` ```{{python}} ```` (the test
harness writes them as ```` ```{python} ````). Run one lesson with
`pixi run test-tutorials 05-pixi`, everything with `pixi run test-tutorials`,
and see `tests/substitutions.yml` for URLs that are swapped in tests.

### What is tested where

Lessons do not carry a "last tested" line: test status is tracked by CI. The
*Tutorials* workflow (`.github/workflows/tutorials.yml`) runs every lesson
after each change to `pages/` and every Monday, on Linux and macOS, and keeps
each run's logs and `summary.json` for 14 days; the run's date and the
versions in each `pixi.lock` say what was tested with what. The
[workflow runs](https://github.com/khan-lab/cbio7501-f26/actions) are the
current status.

| Steps | Tested by |
|-------|-----------|
| Shell commands (`.run`, `.expect-fail`, `.write`) | *Tutorials*, Linux and macOS; locally `pixi run test-tutorials` |
| Git writes and pushes, Docker (`.run-ci`) | *Tutorials*, Linux only (`--ci`) |
| Docker image and Apptainer | *Containers* (`containers.yml`), Linux |
| Pixi environments and tasks on Windows | *OS matrix* (`os-matrix.yml`): the default environment and the template, on Windows, macOS and Linux |
| The finished LTEE project | *LTEE pipeline* (`ltee-pipeline.yml`) |
| Website, credits, internal links / external links | *Website* (`site.yml`, every push) / *External links* (`links-external.yml`, Mondays) |
| PowerShell blocks (native Windows) | not tested: no Windows run of the tutorials |
| Steps that need an account or a cluster (GitHub web pages, Zenodo, Karakoram; `.norun`) | not tested automatically: try them before teaching |

The history of the first build, run locally on macOS before any of these
workflows ran, is the test log in `docs/BUILD_LOG.md`.

### Credit what you adapt

- Only adapt material under CC BY, CC0, MIT or BSD licenses; link anything
  else (for example the Seqera training, CC BY-NC-SA).
- Add an `adapted_from:` entry to the page's front matter (title, url,
  authors, license, accessed, version, changes) and list the same URL on
  `pages/credits.qmd`; `pixi run check-credits` fails otherwise. Pages that are
  entirely our own say `adapted_from: []`.
- Decks list papers and linked figures under `sources:`; the filter builds the
  final Sources slide.
- Embed a third-party figure only if its license allows it (CC BY, CC0):
  copy it into `assets/images/<source>/`, add it to that folder's README and
  to the credits page, and show a credit line with it (on slides:
  `[Figure: NBIS, *Tools for Reproducible Research*, CC BY 4.0]{.fig-credit}`).
- Never embed press photos, journal pages, comics, logos, or anything whose
  origin is unclear: link it with a one-line description, or draw your own.

## Changing the look

Colors are tokens in `assets/css/theme-light.scss` and `theme-dark.scss`
(contrast checked against WCAG AA; keep it that way); rules that use them are in
`styles.scss`, so the dark theme stays designed rather than inverted. Slides
use `slides.scss`. Useful classes: `.fig-credit` (credit line), `.bordered`
(screenshots), `.small`, `.muted`, `.key-box`, `.prompt`, `.quiz`, and
`.code-tight` (dense code on a slide). Mermaid cells in decks need
`%%| eval: true` and `%%| echo: false`, because decks default to `eval: false`.

## Updating software

- Course site: edit `pixi.toml`, run `pixi install`, commit `pixi.lock`.
- Example project: `cd tutorials/ltee-project && pixi upgrade`, then
  `pixi run compare-workflows` and `pixi run reproduce`, and update the
  versions and expected numbers quoted in the lessons' expected output
  (search the lessons for the old version number).
- Pixi version: CI workflows pin `pixi-version`; the devcontainer and the
  Dockerfile in the template pin it too.

## Data

The LTEE data is downloaded from figshare and NCBI (see
`tutorials/ltee-project/metadata/sources.tsv`). If a source moves, update the
URL and keep the checksums: they must not change.
