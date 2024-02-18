# ====================================================================== #
# ============================= FUNCTIONS ============================== #
# ====================================================================== #


import pathlib
import pandas as pd
from bolero_process.atac.bulk import *


# ====================================================================== #
# ============================= PARAMETERS ============================= #
# ====================================================================== #


# reference
ref_prefix = "/home/gcpuser/sky_workdir/ref/hisat2-dna/mm10.hisat2-dna"
blacklist_path = "/ref/blacklist/mm10-blacklist.v2.bed.gz"
chrom_sizes_path = "/ref/mm10/fasta/mm10.main.chrom.sizes"
global_peak_path = "./mm10-cCREs.bed.gz"

# data
samples = [
    "_".join(p.name.split("_")[:-2])
    for p in pathlib.Path("./fastq/").glob("*R1*.fastq.gz")
]


# ====================================================================== #
# =============================== RULES ================================ #
# ====================================================================== #


rule all:
    input:
        expand("bigwig/{sample}.cutsites.norm.bw", sample=samples),
    output:
        "multiqc_report.html",
    shell:
        "multiqc --force ./"


rule trim:
    input:
        r1="fastq/{sample}_R1_001.fastq.gz",
        r2="fastq/{sample}_R2_001.fastq.gz",
    output:
        r1="fastq/{sample}_R1.trim.fq.gz",
        r2="fastq/{sample}_R2.trim.fq.gz",
        json="fastq/{sample}_fastp.json",
        html="fastq/{sample}_fastp.html",
    threads: 2
    shell:
        "fastp -i {input.r1} -I {input.r2} "
        "-o {output.r1} -O {output.r2} "
        "--thread {threads} "
        "-j {output.json} -h {output.html}"


rule mapping:
    input:
        r1="fastq/{sample}_R1.trim.fq.gz",
        r2="fastq/{sample}_R2.trim.fq.gz",
    output:
        bam="bam/{sample}.raw.bam",
        summary="bam/{sample}.hisat2_summary.txt",
    threads: 8
    priority: 50
    shell:
        "hisat2 "
        "-p {threads} "
        "--mm -q --phred33 "
        "--no-spliced-alignment "
        "-X 2000 "
        "-x {ref_prefix} "
        "-1 {input.r1} -2 {input.r2} "
        "--summary-file {output.summary} | "
        "samtools view -1 -bS > {output.bam}"


rule sort:
    input:
        "bam/{sample}.raw.bam",
    output:
        "bam/{sample}.namesort.bam",
    threads: 4
    priority: 50
    shell:
        "samtools sort -n -@ {threads} -m 1G {input} > {output}"


rule genrich:
    input:
        "bam/{sample}.namesort.bam",
    output:
        # peak="count/{sample}.Genrich.narrowPeak",
        # bed="count/{sample}.fragments.bed",
        bedgraph="count/{sample}.cutsites.bedgraph",
    threads: 4
    priority: 50
    shell:
        "Genrich "
        "-j "
        "-d 20 "
        "-y "
        "-r "
        "-e chrM "
        "-E {blacklist_path} "
        "-m 30 "
        "-t {input} "
        "-X "
        # "-o {output.peak} "
        # "-b {output.bed} "
        "-k {output.bedgraph}"
        # -j, Use ATAC-seq mode
        # -d, Expand cut sites to <int> bp
        # -y, Keep unpaired alignments
        # -r, Remove PCR duplicates
        # -e, Comma-separated list of chromosomes to exclude
        # -X, Skip peak-calling


rule zarr:
    input:
        "count/{sample}.cutsites.bedgraph",
    output:
        dir=directory("zarr/{sample}.cutsites.zarr"),
        flag="zarr/{sample}.cutsites.zarr/.success",
    threads: 1
    priority: 50
    run:
        coverage_to_zarr(
            coverage_path=str(input),
            zarr_path=str(output.dir),
            chrom_sizes_path=str(chrom_sizes_path),
            chunk_size=20000000,
        )


rule normzarr:
    input:
        "zarr/{sample}.cutsites.zarr",
    output:
        directory("zarr/{sample}.cutsites.norm.zarr"),
    threads: 1
    priority: 50
    run:
        normalize_zarr(
            zarr_path=str(input),
            peak_path=str(global_peak_path),
            chrom_sizes_path=str(chrom_sizes_path),
            output_zarr_path=str(output),
            chunk_size=20000000,
        )


rule bigwig:
    input:
        "zarr/{sample}.cutsites.norm.zarr",
    output:
        "bigwig/{sample}.cutsites.norm.bw",
    threads: 1
    priority: 50
    run:
        zarr_to_bigwig(zarr_path=str(input), bigwig_path=str(output))
