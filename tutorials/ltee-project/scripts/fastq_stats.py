"""Small summaries of FASTQ files, used by the LTEE report.

Only the Python standard library and pandas are needed. Quality scores are
Phred+33 (Illumina 1.8+), as in the LTEE files.
"""

from itertools import islice
from pathlib import Path

import pandas as pd


def read_fastq(path, max_reads=None):
    """Yield (sequence, quality string) for each read, up to max_reads."""
    with open(path) as fh:
        records = iter(lambda: list(islice(fh, 4)), [])
        for i, lines in enumerate(records):
            if max_reads is not None and i >= max_reads:
                return
            yield lines[1].rstrip("\n"), lines[3].rstrip("\n")


def count_reads(path):
    """Number of reads in a FASTQ file (four lines per read)."""
    with open(path) as fh:
        return sum(1 for _ in fh) // 4


def summarize(path, max_reads=20000):
    """Read count (all reads) and length, GC and quality (first max_reads reads)."""
    lengths, gc, quality = [], 0, 0
    for seq, qual in read_fastq(path, max_reads):
        lengths.append(len(seq))
        gc += seq.count("G") + seq.count("C")
        quality += sum(ord(c) - 33 for c in qual)
    bases = sum(lengths)
    return {
        "file": Path(path).name,
        "reads": count_reads(path),
        "mean_length": bases / len(lengths),
        "gc_percent": 100 * gc / bases,
        "mean_quality": quality / bases,
    }


def quality_by_position(path, max_reads=20000):
    """Mean Phred quality at each read position (1-based)."""
    totals, counts = [], []
    for _, qual in read_fastq(path, max_reads):
        for i, c in enumerate(qual):
            if i == len(totals):
                totals.append(0)
                counts.append(0)
            totals[i] += ord(c) - 33
            counts[i] += 1
    return pd.Series([t / n for t, n in zip(totals, counts)],
                     index=range(1, len(totals) + 1), name=Path(path).name)
