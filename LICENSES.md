# Which license covers what

This repository holds two kinds of material, under two licenses.

| Material | License | File |
|----------|---------|------|
| Code: scripts, Pixi manifests and tasks, workflows (Snakemake, Nextflow), Dockerfiles, CI workflows, the Cookiecutter template, code blocks in the tutorials | MIT | [`LICENSE`](LICENSE) |
| Text and slides: tutorial pages, lecture decks, quiz banks, rubric, figures we made ourselves | Creative Commons Attribution 4.0 International (CC BY 4.0) | [`LICENSE-CC-BY-4.0.txt`](LICENSE-CC-BY-4.0.txt) |

## Material from others

Parts of this workshop are adapted from other open lessons. Those parts keep
their original license and credit:

- The [Sources and credits](pages/credits.qmd) page lists every source
  (authors, link, license, version), the data, the software and the figures
  we link to. Every page of the site links to it from its footer, and every
  slide deck ends with a Sources slide.
- Every adapted page records its sources in its `adapted_from:` front matter
  (source, authors, license, link, what we changed).
- We only adapt material under licenses that allow it (CC BY 4.0, MIT, BSD).
  Material under a non-commercial or share-alike license (for example the
  Seqera Nextflow training, CC BY-NC-SA 4.0) and material whose license we
  could not confirm is linked, never copied.
- Figures from NBIS's *Tools for Reproducible Research* are in
  `assets/images/nbis/` under their own license, CC BY 4.0, with a README of
  their sources; every place that shows one gives the credit line. Other
  third-party images (journal pages, press photos, comics) are not part of
  this repository: the decks link to them with a short description instead.
- The web fonts in `assets/fonts/` (Inter and JetBrains Mono) are under the
  SIL Open Font License 1.1; the license texts are next to them.

## Data

The LTEE example data is not stored in this repository. It is downloaded from
its source: the Data Carpentry subset on figshare
(<https://doi.org/10.6084/m9.figshare.7726454>, CC0) and the *E. coli* REL606
reference genome from NCBI (GenBank CP000819.1). See the credits page for
citations.

## How to attribute this workshop

If you reuse or adapt this material, please credit "CBIO7501 Reproducible and
Open Science workshop, Aziz Khan and contributors", link to the repository,
state the license (CC BY 4.0 for text, MIT for code) and say what you changed.
`CITATION.cff` has the citation details.
