# cookiecutter-repro-project

A [Cookiecutter](https://cookiecutter.readthedocs.io/) template for a small,
reproducible analysis project, used in the CBIO7501 Reproducible and Open
Science workshop (lesson 02 and every lesson after it).

## Use it

You need [Pixi](https://pixi.prefix.dev/latest/). Pixi downloads Cookiecutter
into a temporary environment, so nothing else has to be installed:

```bash
pixi exec cookiecutter gh:khan-lab/cbio7501-f26 --directory templates/cookiecutter-repro-project
```

Answer the questions (press Enter to keep a default). You get a folder named
after your project with this layout:

```
my-project/
├── README.md            what the project is and how to reproduce it
├── LICENSE              the license you chose
├── CITATION.cff         how to cite it
├── pixi.toml            software environment (pixi.lock appears after `pixi install`)
├── .gitignore           keeps data, results and environments out of Git
├── data/raw/            raw data, read-only, downloaded by a script
├── data/processed/      data derived by code
├── metadata/            sample sheet, sources, checksums
├── scripts/             your code
├── config/              parameters            (only with workflow stubs)
├── workflow/            Snakemake / Nextflow  (only with workflow stubs)
├── notebooks/           Jupyter notebooks
├── reports/             Quarto reports
├── results/             figures, tables, logs (regenerated)
├── docs/                longer documentation
├── envs/                Conda exports for people without Pixi
├── containers/          Dockerfile, Apptainer (only with container stubs)
└── .github/workflows/reproduce.yml   CI: reproduce from a clean clone
```

Each folder has a `README.md` that explains what goes in it.

## Questions you are asked

| Question | Used for |
|----------|----------|
| `project_name`, `short_description` | README, CITATION.cff, pixi.toml |
| `project_slug` | folder name and repository name |
| `author_given_names`, `author_family_names`, `author_email`, `author_orcid` | LICENSE, CITATION.cff, README |
| `github_username` | repository URL in CITATION.cff |
| `license` | which LICENSE file is written (MIT, BSD-3-Clause, Apache-2.0, CC-BY-4.0, or none yet) |
| `primary_language` | Python only for now |
| `include_workflow_stubs`, `include_container_stubs` | keep or drop `workflow/`, `config/` and `containers/` |

Run without questions, keeping every default (useful in tests):

```bash
pixi exec cookiecutter --no-input gh:khan-lab/cbio7501-f26 --directory templates/cookiecutter-repro-project project_name="My project"
```

## Why Cookiecutter and not Copier

We compared both (October 2026: Cookiecutter 2.7.1, Copier 9.19.1). Copier's
main extra is `copier update`, which brings template changes into existing
projects, but it needs the template versioned with Git tags *and* the new
project under Git. Learners create their project in lesson 02, one lesson
before Git is taught, and need one command that works without Git. Cookiecutter does
that, is the tool the two templates we learned from use, and keeps the
template easy to read. If template updates for running projects become
important, Copier (or `cruft` on top of Cookiecutter) is the upgrade path.

## Credits

Inspired by (no files copied):
[mkrapp/cookiecutter-reproducible-science](https://github.com/mkrapp/cookiecutter-reproducible-science)
(BSD 3-Clause, Mario Krapp) and
[bios259/cookie-for-reproducible-research](https://github.com/bios259/cookie-for-reproducible-research)
(no license stated), and by Noble (2009) "A quick guide to organizing
computational biology projects" and Wilson et al. (2017) "Good enough
practices in scientific computing". License texts in `.licenses/` come from
[choosealicense.com](https://github.com/github/choosealicense.com) and
Creative Commons.

License of this template: MIT.
