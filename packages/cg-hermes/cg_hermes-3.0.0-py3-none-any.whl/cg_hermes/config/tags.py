ALIGNMENT_COMMON = {
    "bam": {
        "description": "Alignment file in BAM format",
    },
    "bam-index": {
        "description": "Index file for alignment file in BAM format",
    },
    "bam-mt": {
        "description": "Alignment file in BAM format holding the reaads from chrMT",
    },
    "cram": {
        "description": "Alignment file in CRAM format",
    },
    "cram-index": {
        "description": "Index file for alignment file in CRAM format",
    },
}

RAW_DATA = {
    "fastq": {"description": "Files with raw data in fastq format"},
    "fasta": {"description": "Files with raw data in fasta format"},
    "forward-strand": {"description": "Reads from forward strand"},
    "reverse-strand": {"description": "Reads from reverse strand"},
    "unpaired-reads": {"description": "Reads that could not be paired"},
    "rna": {"description": "Data generated from RNA samples"},
}

VARIANT_COMMON = {
    "cnv": {"description": "Copy number variants"},
    "mobile-elements": {"description": "Mobile elements"},
    "normal": {"description": "Associated with normal sample"},
    "germline": {"description": "Associated with germline variants"},
    "somatic": {"description": "Associated with somatic variants"},
    "rhocall-viz": {"description": "Runs of homozygosity index"},
    "smn-calling": {"description": "Copy number calls for the SMN gene"},
    "snv": {"description": "Single nucleotide variants and short indels"},
    "snv-bcf": {"description": "Gvcf including all SNV variants"},
    "snv-gbcf": {"description": "Gvcf including all SNV variants"},
    "sv-bcf": {"description": "Gvcf including all SV variants"},
    "sv-vcf": {"description": "Variant call formated file with structural variants"},
    "sv-vcf-index": {"description": "Following index"},
    "telomere-calling": {"description": "Variants from telomere calling"},
    "tmb": {"description": "Tumor mutational burden information"},
    "tumor": {"description": "Associated with tumor sample"},
    "upd": {"description": "Uniparental disomy variants"},
    "vcf": {"description": "Variant call formated file"},
    "vcf-index": {"description": "Following index"},
    "vcf-snv": {"description": "SNV variant call formated file"},
    "vcf-snv-index": {"description": "Following index"},
    "sv": {"description": "Structural variants"},
    "vcf-sv": {"description": "SV variant call formated file"},
    "vcf-sv-index": {"description": "Following index"},
    "vcf-snv-filtered": {"description": "SNV variants filtered by BALSAMIC"},
    "vcf-snv-filtered-index": {"description": "Following index"},
    "vcf-snv-clinical": {"description": "SNV variants from clinical panels"},
    "vcf-snv-clinical-index": {"description": "Following index"},
    "vcf-snv-research": {"description": "SNV variants from whole genome"},
    "vcf-snv-research-index": {"description": "Following index"},
    "vcf-str": {"description": "Short tandem repeat variants"},
    "vcf-str-index": {"description": "Following index"},
    "vcf-sv-clinical": {"description": "SV variants from clinical panels"},
    "vcf-sv-clinical-index": {"description": "Following index"},
    "vcf-sv-research": {"description": "SV variants from whole genome"},
    "vcf-sv-research-index": {"description": "Following index"},
    "vcf-umi-snv": {"description": "Raw SNV UMI variant formatted file"},
    "vcf-umi-snv-index": {"description": "Following index"},
    "vcf-umi-snv-research": {"description": "SNV UMI variant formatted file"},
    "vcf-umi-snv-research-index": {"description": "Following index"},
    "vcf-umi-snv-clinical": {"description": "SNV UMI variants from clinical panels"},
    "vcf-umi-snv-clinical-index": {"description": "Following index"},
    "vcf-snv-germline-tumor": {"description": "SNV germline tumor variants"},
    "vcf-snv-germline-tumor-index": {"description": "Following index"},
    "vcf-snv-germline-normal": {"description": "SNV germline normal variants"},
    "vcf-snv-germline-normal-index": {"description": "Following index"},
    "vcf-sv-germline-tumor": {"description": "SV germline tumor variants"},
    "vcf-sv-germline-tumor-index": {"description": "Following index"},
    "vcf-sv-germline-normal": {"description": "SV germline normal variants"},
    "vcf-sv-germline-normal-index": {"description": "Following index"},
    "vcf2cytosure": {"description": "Conversion from vcf format to cytosure format"},
    "variants": {"description": "File pertaining variant information in some way"},
}

FAMILY_COMMON = {
    "pedigree": {"description": "Pedigree information"},
    "ped": {"description": "Pedigree information"},
}

REPORTING_COMMON = {
    "audit": {"description": "Audit file"},
    "csv": {"description": "Comma separated values"},
    "deliverable": {"description": "Deliverables file"},
    "delivery-report": {"description": "Delivery report with result for upload to Scout"},
    "multiqc-html": {"description": "Multiqc report for the run in html format"},
    "multiqc-json": {"description": "Multiqc report for the run in json format"},
    "pdf": {"description": "Portable document format"},
    "qc-report": {"description": "Results and QC"},
    "sambamba-depth": {"description": "Coverage information from sambamba"},
    "summary": {"description": "Overview file without detailed information"},
    "tsv": {"description": "Tab separated values"},
    "vcf-report": {"description": "Results and QC from variant calling"},
    "cnv-report": {"description": "CNV variant calling report"},
    "software-versions": {"description": "Versions of software used in analysis"},
    "gene-counts": {"description": "STAR read counts output per gene"},
}

VALIDATIONS_COMMON = {
    "ped-check": {"description": "Results from pedigree validation"},
    "qc-metrics": {"description": "QC metrics from analysis"},
    "sex-check": {"description": "Results from sex validation"},
}

ANALYSIS_COMMON = {
    "assembly": {"description": "Assembly"},
    "autozyg": {"description": "Autozygous region"},
    "bed": {"description": "Bed file"},
    "bed-index": {"description": "Following index"},
    "bigwig": {"description": "Bigwig formated file"},
    "clinical": {"description": "Clinical subset"},
    "config": {"description": "Config file"},
    "coverage": {"description": "Output with coverage information"},
    "scatter-plot": {"description": "Scatter plot"},
    "circular-plot": {"description": "Circular plot"},
    "profile-plot": {"description": "Copy number profile plot"},
    "raw-profile-plot": {"description": "Copy number profile without rounding to whole numbers"},
    "aspcf-plot": {"description": "Plot of LogR and BAF values"},
    "sunrise-plot": {"description": "Sunrise plot"},
    "tumor-plot": {"description": "Plot of LogR and BAF values for tumor sample"},
    "germline-plot": {"description": "Plot of LogR and BAF values for normal sample"},
    "filtered": {"description": "Filtered data"},
    "fracsnp": {"description": "Fraction of reads with snp"},
    "fusion": {"description": "Fusion transcripts"},
    "genes": {"description": "Related to genes"},
    "junction": {"description": "Junction data"},
    "metrics": {"description": "Data metrics"},
    "first-pass": {"description": "Data metrics first pass"},
    "second-pass": {"description": "Data metrics second pass"},
    "reference-info": {"description": "Information about references used in analysis"},
    "regions": {"description": "Output for regions"},
    "research": {"description": "Research set"},
    "segments": {"description": "Output for segments"},
    "sites": {"description": "Output for sites"},
    "tcov": {"description": "Coverage output"},
    "tiddit-coverage": {"description": "Coverage output from tiddit"},
    "visualization": {"description": "Visualizes data"},
    "umi": {"description": "Files related to UMI workflow"},
    "umi-cram": {"description": "UMI consensus filtered cram file"},
    "umi-cram-index": {"description": "Index for the UMI consensus filtered cram file"},
    "qc-cram": {"description": "QC alignment file in CRAM format"},
    "qc-cram-index": {"description": "QC index file for alignment file in CRAM format"},
    "vcf-fusion": {"description": "Converted RNA fusion file to SV VCF"},
}

TOOLS = {
    "arriba": {"description": "Fusion caller"},
    "ascatngs": {"description": "Tool to identify somatically acquired copy-number alterations"},
    "cnvpytor": {"description": "Tool for CNV/CNA analysis from depth-of-coverage by mapped reads"},
    "asereadcounter": {"description": "Count reads mapping to heterozygous sites"},
    "chanjo": {"description": "Tool to keep track of coverage over specific regions"},
    "chromograph": {"description": "Tool to create PNG images from BED and WIG files from mikaell"},
    "cnvkit": {"description": "Tool to call copy number variations"},
    "cyrius": {"description": "Tool to call the problematic CYP2D6 gene"},
    "deepvariant": {"description": "Variantcaller"},
    "delly": {"description": "Cancer structural variant prediction tool"},
    "deseq2": {"description": "Differential expression analysis with DESeq2"},
    "dnascope": {"description": "Call snv indels"},
    "fusioncatcher": {"description": "Fusion caller"},
    "fusioncatcher-summary": {"description": "Fusion caller summary"},
    "fusioninspector": {"description": "Fusion inspection"},
    "expansionhunter": {"description": "Call repeat expansions"},
    "genotyper": {"description": "SNV indel caller from sention"},
    "gens": {"description": "CNV visualization tool"},
    "gffcompare": {"description": "Compare gff files"},
    "haplotype-caller": {"description": "Call snv and indels"},
    "manta": {"description": "Tool to call structural variants"},
    "mitodel": {"description": "Tool to identify mitochondrial deletion signatures"},
    "peddy": {"description": "Tool to check pedigree and ancestral relations"},
    "picard": {"description": "Picard set of bioinformatic tools"},
    "pizzly": {"description": "Fusion caller"},
    "retroseq": {"description": "Mobile element caller"},
    "salmon-quant": {"description": "Transcript quantification"},
    "sention": {"description": "Sention algorithm"},
    "squid": {"description": "Fusion caller"},
    "star-fusion": {"description": "Fusion caller"},
    "stringtie": {"description": "Transcript assembler"},
    "svdb": {"description": "Tool to merge SV vcf files from multiple variant callers"},
    "tiddit": {"description": "Tool to identify chromosomal rearrangements"},
    "tnscope": {"description": "Call snv indels"},
    "tnscope-umi": {"description": "Call snv indels for umi"},
    "upd": {"description": "Uniparent disomy caller from bjhall"},
    "vardict": {"description": "Cancer variant caller"},
    "wisecondor": {"description": "NIPT caller"},
    "nextclade": {"description": "Viral genome clade assignment"},
}

MIP_SPECIFIC = {
    "exe-ver": {"description": "Executable versions"},
    "mip-analyse": {"description": "MIP information about analysis"},
    "mip-config": {"description": "MIP configs for analysis"},
    "mip-log": {"description": "Logs for MIP analysis"},
    "pedigree-yaml": {"description": "YAML file with pedigree information"},
    "sample-info": {"description": "MIP info file about samples"},
    "variant-catalog": {"description": "Variant catalog used with expansionhunter"},
}

BALSAMIC_SPECIFIC = {
    "balsamic-config": {"description": "Balsamic configs for analysis"},
    "balsamic-dag": {"description": "Balsamic run schema"},
    "balsamic-report": {"description": "Report from analysis"},
}

MICROSALT_SPECIFIC = {
    "microsalt-config": {"description": "Config settings for microsalt analysis"},
    "microsalt-log": {"description": "SLURM log for microsalt analysis"},
    "typing-report": {"description": "Results from bacterial typing"},
}

MUTANT_SPECIFIC = {
    "mutant-config": {"description": "Config settings for mutant analysis"},
    "mutant-log": {"description": "SLURM log for mutant analysis"},
    "pangolin": {"description": "Pangolin specific output"},
    "typing-report": {"description": "Results from typing"},
    "typing-summary": {"description": "Summary of results from typing"},
    "fohm-delivery": {"description": "Relevant for FoHM"},
    "ks-delivery": {"description": "Relevant for Karolinska hospital/microbial routine"},
    "komplettering": {"description": "Filetype specific for national uploading of microbial data"},
    "consensus": {"description": "Consensus sequence"},
    "ks-results": {"description": "KS modification of pangolin typing results"},
    "ks-aux-results": {"description": "KS modification of pangolin called variants"},
    "pangolin-typing": {"description": "Pangolin typing results"},
    "artic-sum": {"description": "GMS-Artic summary file"},
    "artic-var": {"description": "GMS-Artic variant file"},
    "artic-type": {"description": "GMS-Artic typing file"},
    "artic-qc": {"description": "GMS-Artic QC file"},
    "artic-json": {"description": "GMS-Artic json file"},
    "vcf-covid": {"description": "VCF file containing covid data. Distinction req. by production"},
    "instrument-properties": {"description": "Sequencing metadata"},
    "consensus-sample": {"description": "Separate sample consensus fasta"},
    "pangolin-typing-fohm": {
        "description": "Pangolin typing report with only qc_pass samples included"
    },
}

RNAFUSION_SPECIFIC = {
    "arriba-visualisation": {"description": "Arriba visualization"},
    "fusionreport": {"description": "Fusion-report analysis"},
    "fusioninspector-html": {"description": "Fusioninspector report"},
}

NEXTFLOW_SPECIFIC = {
    "samplesheet-valid": {"description": "Validated samplesheet"},
    "software-versions": {"description": "List of all software used and their versions"},
}

AVAILABLE_USAGES = {
    "audit",
    "cg",
    "chanjo",
    "deliver",
    "genotype",
    "nipt",
    "scout",
    "storage",
    "vogue",
}

COMMON_TAG_CATEGORIES = {
    "alignment_tags": ALIGNMENT_COMMON,
    "analysis_tags": ANALYSIS_COMMON,
    "family_tags": FAMILY_COMMON,
    "raw_data": RAW_DATA,
    "reporting_tags": REPORTING_COMMON,
    "tool_tags": TOOLS,
    "validation_tags": VALIDATIONS_COMMON,
    "variant_tags": VARIANT_COMMON,
}

ALL_TAG_CATEGORIES = [
    ALIGNMENT_COMMON,
    ANALYSIS_COMMON,
    BALSAMIC_SPECIFIC,
    FAMILY_COMMON,
    MIP_SPECIFIC,
    MICROSALT_SPECIFIC,
    MUTANT_SPECIFIC,
    NEXTFLOW_SPECIFIC,
    RNAFUSION_SPECIFIC,
    RAW_DATA,
    REPORTING_COMMON,
    TOOLS,
    VALIDATIONS_COMMON,
    VARIANT_COMMON,
]

ALL_TAGS = {tag for category in ALL_TAG_CATEGORIES for tag in category.keys()}

if __name__ == "__main__":
    print(ALL_TAGS)
