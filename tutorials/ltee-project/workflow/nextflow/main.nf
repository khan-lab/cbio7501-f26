// LTEE variant calling with Nextflow.
//
// Same steps and tool options as workflow/Snakefile, which follow Data
// Carpentry "Wrangling Genomics" (variant calling episode, CC BY 4.0,
// https://datacarpentry.github.io/wrangling-genomics/04-variant_calling.html),
// with FastQC and MultiQC added at the start.
//
// Run from the project folder, with the same settings file as Snakemake:
//   pixi run run-nextflow
// (or: pixi run -e pipeline nextflow run workflow/nextflow/main.nf -params-file config/config.yaml)
// Results go to results/nextflow/ (set in workflow/nextflow/nextflow.config).

params {
    // Tab-separated sample sheet with sample, fastq_1 and fastq_2 columns
    samples: Path = 'metadata/samples.tsv'
    // Gzipped reference genome (E. coli REL606)
    reference_gz: Path = 'data/raw/reference/ecoli_rel606.fasta.gz'
    // Extra bwa mem options (-K makes alignments independent of the thread count)
    bwa_extra: String = '-K 10000000'
    // Minimum read depth for the final filter (vcfutils.pl varFilter -d)
    min_depth: Integer = 2
    // Depth thresholds compared for the analysis question
    sensitivity_depths: List<Integer> = [2, 5, 10, 15]
}

process FASTQC {
    tag "${sample}"

    input:
    tuple val(sample), path(reads)

    output:
    path '*_fastqc.html', emit: html
    path '*_fastqc.zip', emit: zip

    script:
    """
    fastqc --quiet ${reads}
    """
}

process MULTIQC {
    input:
    path zips

    output:
    path 'multiqc_report.html'

    script:
    """
    multiqc --force ${zips}
    """
}

process PREPARE_REFERENCE {
    input:
    path reference_gz

    output:
    tuple path('ecoli_rel606.fasta'), path('ecoli_rel606.fasta.*')

    script:
    """
    gunzip -c ${reference_gz} > ecoli_rel606.fasta
    bwa index ecoli_rel606.fasta
    """
}

process ALIGN {
    tag "${sample}"
    cpus 4

    input:
    tuple val(sample), path(reads)
    tuple path(genome), path(index)
    val bwa_extra

    output:
    tuple val(sample), path("${sample}.aligned.sorted.bam"), path("${sample}.aligned.sorted.bam.bai")

    script:
    """
    bwa mem -t ${task.cpus} ${bwa_extra} ${genome} ${reads[0]} ${reads[1]} > ${sample}.aligned.sam
    samtools view -S -b ${sample}.aligned.sam > ${sample}.aligned.bam
    samtools sort -o ${sample}.aligned.sorted.bam ${sample}.aligned.bam
    samtools index ${sample}.aligned.sorted.bam
    """
}

process FLAGSTAT {
    tag "${sample}"

    input:
    tuple val(sample), path(bam), path(bai)

    output:
    path "${sample}.flagstat.txt"

    script:
    """
    samtools flagstat ${bam} > ${sample}.flagstat.txt
    """
}

process CALL_VARIANTS {
    tag "${sample}"

    input:
    tuple val(sample), path(bam), path(bai)
    tuple path(genome), path(index)

    output:
    tuple val(sample), path("${sample}_variants.vcf")

    script:
    """
    bcftools mpileup -O b -o ${sample}_raw.bcf -f ${genome} ${bam}
    bcftools call --ploidy 1 -m -v -o ${sample}_variants.vcf ${sample}_raw.bcf
    """
}

process FILTER_VARIANTS {
    tag "${sample}"

    input:
    tuple val(sample), path(variants)
    val min_depth

    output:
    tuple val(sample), path("${sample}_final_variants.vcf")

    script:
    """
    vcfutils.pl varFilter -d ${min_depth} ${variants} > ${sample}_final_variants.vcf
    """
}

process DEPTH_SENSITIVITY {
    tag "${sample} d${depth}"

    input:
    tuple val(sample), path(variants), val(depth)

    output:
    path "${sample}_d${depth}.vcf"

    script:
    """
    vcfutils.pl varFilter -d ${depth} ${variants} > ${sample}_d${depth}.vcf
    """
}

process VARIANT_STATS {
    tag "${sample}"

    input:
    tuple val(sample), path(final_variants)

    output:
    path "${sample}.bcftools-stats.txt"

    script:
    """
    bcftools stats ${final_variants} > ${sample}.bcftools-stats.txt
    """
}

workflow {
    main:
    ch_samples = channel.fromPath(params.samples)
        .splitCsv(header: true, sep: '\t')
        .map { row -> tuple(row.sample, [file(row.fastq_1), file(row.fastq_2)]) }

    ch_fastqc = FASTQC(ch_samples)
    ch_multiqc = MULTIQC(ch_fastqc.zip.collect())

    ch_reference = PREPARE_REFERENCE(params.reference_gz)
    ch_bam = ALIGN(ch_samples, ch_reference, params.bwa_extra)
    ch_flagstat = FLAGSTAT(ch_bam)
    ch_variants = CALL_VARIANTS(ch_bam, ch_reference)
    ch_final = FILTER_VARIANTS(ch_variants, params.min_depth)
    ch_stats = VARIANT_STATS(ch_final)
    ch_sensitivity = DEPTH_SENSITIVITY(ch_variants.combine(channel.fromList(params.sensitivity_depths)))

    publish:
    fastqc = ch_fastqc.html.mix(ch_fastqc.zip)
    multiqc = ch_multiqc
    bam = ch_bam
    variants = ch_variants
    final_variants = ch_final
    stats = ch_flagstat.mix(ch_stats)
    sensitivity = ch_sensitivity
}

output {
    fastqc {
        path 'qc/fastqc'
    }
    multiqc {
        path 'qc/multiqc'
    }
    bam {
        path 'bam'
    }
    variants {
        path 'bcf'
    }
    final_variants {
        path 'vcf'
    }
    stats {
        path 'stats'
    }
    sensitivity {
        path 'sensitivity'
    }
}
