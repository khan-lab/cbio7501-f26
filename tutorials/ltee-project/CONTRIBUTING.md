# Contributing

Thank you for helping. This is a small research project, so the process is simple:

1. Open an issue describing the problem or idea before larger changes.
2. Fork the repository, make a branch, and check that `pixi run reproduce`
   still works on your computer.
3. Open a pull request. The *Reproduce* check must pass before merging.

Please keep raw data out of Git (`data/raw/` is downloaded by
`scripts/download_data.py`), commit `pixi.toml` and `pixi.lock` together, and
record analysis decisions in `docs/decisions.md`.
