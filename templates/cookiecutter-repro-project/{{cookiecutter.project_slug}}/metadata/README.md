# metadata

Small text files that describe the data. They are committed to Git.

Typical files:

- `samples.tsv`: one row per sample (ID, source accession, condition, file names).
- `sources.tsv`: where each raw file is downloaded from, with the provider's checksum.
- `checksums.sha256`: checksums of the raw files you keep, so anyone can check
  they have the same data (`shasum -a 256 -c metadata/checksums.sha256`).
- `README.md` (this file): a data dictionary that explains every column.
