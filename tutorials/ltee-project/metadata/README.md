# metadata

Files that describe the raw data. They are small, written by hand and committed.

## sources.tsv

Where each raw file comes from. Columns: `name`; `url` (download link);
`md5` (checksum published by the provider: figshare record 7726454 and
NCBI's md5checksums.txt, copied 2026-10-24); `unpack` (`tar` = unpack the
archive, `none` = keep the file as is); `dest` (where it goes in the project).

## checksums.sha256

SHA-256 checksum of every raw file we keep. Check with
`sha256sum -c metadata/checksums.sha256`.

## samples.tsv

One row per sample.

| Column | Meaning |
|--------|---------|
| sample | SRA run accession, also used in all file names |
| strain | LTEE clone name (REL…) |
| generation | generation at which the clone was frozen |
| population | LTEE population (all Ara-3 here) |
| mutator | hypermutability status (`None` or `plus`) |
| cit | can use citrate (`plus`) or not known (`unknown`) |
| fastq_1, fastq_2 | read 1 and read 2 FASTQ files, relative to the project folder |

Source of the sample information: Data Carpentry, *Wrangling Genomics*,
`Ecoli_metadata_composite.csv` (CC BY 4.0), from Tenaillon et al. 2016,
*Nature* 536:165, <https://doi.org/10.1038/nature18959>. Runs are in NCBI
BioProject PRJNA295606.
