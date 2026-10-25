# data/raw

Raw data exactly as you received it.

- **Never edit these files.** If something needs fixing, fix it in code and
  write the result to `data/processed/`.
- Get the files with a script (for example `pixi run download`), not by hand,
  so anyone can get the same files.
- Record where each file comes from and its checksum in `metadata/`.
- The files are not committed to Git (see `.gitignore`); the download script
  and the checksums are.
