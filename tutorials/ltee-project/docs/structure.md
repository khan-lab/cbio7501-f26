# Project structure

| Folder | What goes in it | Rule |
|--------|-----------------|------|
| `data/raw/` | Raw data, downloaded by `scripts/download_data.py` | Read-only, not committed |
| `data/processed/` | Data derived from raw data (decompressed, indexed reference) | Rebuilt by the workflow |
| `metadata/` | Sample sheet, data sources, checksums, data dictionary | Committed |
| `scripts/` | Download, comparison and helper code | Committed |
| `config/` | Workflow settings (`config.yaml`), shared by Snakemake and Nextflow | Committed |
| `workflow/` | `Snakefile` and `nextflow/` | Committed |
| `notebooks/` | Exploration (`explore-reads.ipynb`), outputs cleared | Committed |
| `reports/` | Quarto report source and bibliography | Source committed, HTML not |
| `results/` | Everything the workflow produces | Rebuilt, not committed |
| `docs/` | This file, the decision log | Committed |
| `envs/` | Conda exports of the Pixi environments | Generated |
| `containers/` | `Dockerfile` and `apptainer.def`, built from `pixi.lock` | Committed |
| `.github/workflows/` | The reproduce-from-a-clean-clone check | Committed |
