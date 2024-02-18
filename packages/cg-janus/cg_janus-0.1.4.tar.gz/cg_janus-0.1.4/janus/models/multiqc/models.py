"""Models for the MultiQC intermediate JSON files."""

from pydantic import BaseModel, Field


class PicardDups(BaseModel):
    UNPAIRED_READS_EXAMINED: float
    READ_PAIRS_EXAMINED: float
    SECONDARY_OR_SUPPLEMENTARY_RDS: float
    UNMAPPED_READS: float
    UNPAIRED_READ_DUPLICATES: float
    READ_PAIR_DUPLICATES: float
    READ_PAIR_OPTICAL_DUPLICATES: float
    PERCENT_DUPLICATION: float
    ESTIMATED_LIBRARY_SIZE: float


class PicardInsertSize(BaseModel):
    MEDIAN_INSERT_SIZE: float
    MODE_INSERT_SIZE: float
    MEDIAN_ABSOLUTE_DEVIATION: float
    MIN_INSERT_SIZE: float
    MAX_INSERT_SIZE: float
    MEAN_INSERT_SIZE: float
    STANDARD_DEVIATION: float
    READ_PAIRS: float
    PAIR_ORIENTATION: str
    WIDTH_OF_10_PERCENT: float
    WIDTH_OF_20_PERCENT: float
    WIDTH_OF_30_PERCENT: float
    WIDTH_OF_40_PERCENT: float
    WIDTH_OF_50_PERCENT: float
    WIDTH_OF_60_PERCENT: float
    WIDTH_OF_70_PERCENT: float
    WIDTH_OF_80_PERCENT: float
    WIDTH_OF_90_PERCENT: float
    WIDTH_OF_95_PERCENT: float
    WIDTH_OF_99_PERCENT: float


class FastpBeforeFiltering(BaseModel):
    total_reads: int
    total_bases: int
    q20_bases: int
    q30_bases: int
    q20_rate: float
    q30_rate: float
    read1_mean_length: int
    read2_mean_length: int
    gc_content: float


class FastpAfterFiltering(BaseModel):
    total_reads: int
    total_bases: int
    q20_bases: int
    q30_bases: int
    q20_rate: float
    q30_rate: float
    read1_mean_length: int
    read2_mean_length: int
    gc_content: float


class Fastp(BaseModel):
    before_filtering: FastpBeforeFiltering
    after_filtering: FastpAfterFiltering


class SamtoolsStats(BaseModel):
    raw_total_sequences: float
    filtered_sequences: float
    sequences: float
    is_sorted: float
    first_fragments: float = Field(..., alias="1st_fragments")
    last_fragments: float
    reads_mapped: float
    reads_mapped_and_paired: float
    reads_unmapped: float
    reads_properly_paired: float
    reads_paired: float
    reads_duplicated: float
    reads_MQ0: float
    reads_QC_failed: float
    non_primary_alignments: float = Field(..., alias="non-primary_alignments")
    supplementary_alignments: float
    total_length: float
    total_first_fragment_length: float
    total_last_fragment_length: float
    bases_mapped: float
    bases_trimmed: float
    bases_duplicated: float
    mismatches: float
    error_rate: float
    average_length: float
    average_first_fragment_length: float
    average_last_fragment_length: float
    maximum_length: float
    maximum_first_fragment_length: float
    maximum_last_fragment_length: float
    average_quality: float
    insert_size_average: float
    insert_size_standard_deviation: float
    inward_oriented_pairs: float
    outward_oriented_pairs: float
    pairs_with_other_orientation: float
    pairs_on_different_chromosomes: float
    percentage_of_properly_paired_reads: float = Field(
        ..., alias="percentage_of_properly_paired_reads_(%)"
    )
    reads_mapped_percent: float
    reads_mapped_and_paired_percent: float
    reads_unmapped_percent: float
    reads_properly_paired_percent: float
    reads_paired_percent: float
    reads_duplicated_percent: float
    reads_MQ0_percent: float
    reads_QC_failed_percent: float


class PicardHsMetrics(BaseModel):
    BAIT_SET: str
    BAIT_TERRITORY: float
    BAIT_DESIGN_EFFICIENCY: float
    ON_BAIT_BASES: float
    NEAR_BAIT_BASES: float
    OFF_BAIT_BASES: float
    PCT_SELECTED_BASES: float
    PCT_OFF_BAIT: float
    ON_BAIT_VS_SELECTED: float
    MEAN_BAIT_COVERAGE: float
    PCT_USABLE_BASES_ON_BAIT: float
    PCT_USABLE_BASES_ON_TARGET: float
    FOLD_ENRICHMENT: float
    HS_LIBRARY_SIZE: float
    HS_PENALTY_10X: float
    HS_PENALTY_20X: float
    HS_PENALTY_30X: float
    HS_PENALTY_40X: float
    HS_PENALTY_50X: float
    HS_PENALTY_100X: float
    TARGET_TERRITORY: float
    GENOME_SIZE: float
    TOTAL_READS: float
    PF_READS: float
    PF_BASES: float
    PF_UNIQUE_READS: float
    PF_UQ_READS_ALIGNED: float
    PF_BASES_ALIGNED: float
    PF_UQ_BASES_ALIGNED: float
    ON_TARGET_BASES: float
    PCT_PF_READS: float
    PCT_PF_UQ_READS: float
    PCT_PF_UQ_READS_ALIGNED: float
    MEAN_TARGET_COVERAGE: float
    MEDIAN_TARGET_COVERAGE: float
    MAX_TARGET_COVERAGE: float
    MIN_TARGET_COVERAGE: float
    ZERO_CVG_TARGETS_PCT: float
    PCT_EXC_DUPE: float
    PCT_EXC_ADAPTER: float
    PCT_EXC_MAPQ: float
    PCT_EXC_BASEQ: float
    PCT_EXC_OVERLAP: float
    PCT_EXC_OFF_TARGET: float
    FOLD_80_BASE_PENALTY: float
    PCT_TARGET_BASES_1X: float
    PCT_TARGET_BASES_2X: float
    PCT_TARGET_BASES_10X: float
    PCT_TARGET_BASES_20X: float
    PCT_TARGET_BASES_30X: float
    PCT_TARGET_BASES_40X: float
    PCT_TARGET_BASES_50X: float
    PCT_TARGET_BASES_100X: float
    PCT_TARGET_BASES_250X: float
    PCT_TARGET_BASES_500X: float
    PCT_TARGET_BASES_1000X: float
    PCT_TARGET_BASES_2500X: float
    PCT_TARGET_BASES_5000X: float
    PCT_TARGET_BASES_10000X: float
    PCT_TARGET_BASES_25000X: float
    PCT_TARGET_BASES_50000X: float
    PCT_TARGET_BASES_100000X: float
    AT_DROPOUT: float
    GC_DROPOUT: float
    HET_SNP_SENSITIVITY: float
    HET_SNP_Q: float


class PicardAlignmentSummary(BaseModel):
    CATEGORY: str
    TOTAL_READS: float
    PF_READS: float
    PCT_PF_READS: float
    PF_NOISE_READS: float
    PF_READS_ALIGNED: float
    PCT_PF_READS_ALIGNED: float
    PF_ALIGNED_BASES: float
    PF_HQ_ALIGNED_READS: float
    PF_HQ_ALIGNED_BASES: float
    PF_HQ_ALIGNED_Q20_BASES: float
    PF_HQ_MEDIAN_MISMATCHES: float
    PF_MISMATCH_RATE: float
    PF_HQ_ERROR_RATE: float
    PF_INDEL_RATE: float
    MEAN_READ_LENGTH: float
    SD_READ_LENGTH: float
    MEDIAN_READ_LENGTH: float
    MAD_READ_LENGTH: float
    MIN_READ_LENGTH: float
    MAX_READ_LENGTH: float
    READS_ALIGNED_IN_PAIRS: float
    PCT_READS_ALIGNED_IN_PAIRS: float
    PF_READS_IMPROPER_PAIRS: float
    PCT_PF_READS_IMPROPER_PAIRS: float
    BAD_CYCLES: float
    STRAND_BALANCE: float
    PCT_CHIMERAS: float
    PCT_ADAPTER: float
    PCT_SOFTCLIP: float
    PCT_HARDCLIP: float
    AVG_POS_3PRIME_SOFTCLIP_LENGTH: float


class SomalierIndividual(BaseModel):
    family_id: str
    paternal_id: float
    maternal_id: float
    sex: float
    phenotype: float
    original_pedigree_sex: float
    gt_depth_mean: float
    gt_depth_sd: float
    depth_mean: float
    depth_sd: float
    ab_mean: float
    ab_std: float
    n_hom_ref: float
    n_het: float
    n_hom_alt: float
    n_unknown: float
    p_middling_ab: float
    X_depth_mean: float
    X_n: float
    X_hom_ref: float
    X_het: float
    X_hom_alt: float
    Y_depth_mean: float
    Y_n: float


class SomalierComparison(BaseModel):
    relatedness: float
    ibs0: float
    ibs2: float
    hom_concordance: float
    hets_a: float
    hets_b: float
    hets_ab: float
    shared_hets: float
    hom_alts_a: float
    hom_alts_b: float
    shared_hom_alts: float
    n: float
    x_ibs0: float
    x_ibs2: float
    expected_relatedness: float


class PicardWGSMetrics(BaseModel):
    GENOME_TERRITORY: float
    MEAN_COVERAGE: float
    SD_COVERAGE: float
    MEDIAN_COVERAGE: float
    MAD_COVERAGE: float
    PCT_EXC_ADAPTER: float
    PCT_EXC_MAPQ: float
    PCT_EXC_DUPE: float
    PCT_EXC_UNPAIRED: float
    PCT_EXC_BASEQ: float
    PCT_EXC_OVERLAP: float
    PCT_EXC_CAPPED: float
    PCT_EXC_TOTAL: float
    PCT_1X: float
    PCT_5X: float
    PCT_10X: float
    PCT_15X: float
    PCT_20X: float
    PCT_25X: float
    PCT_30X: float
    PCT_40X: float
    PCT_50X: float
    PCT_60X: float
    PCT_70X: float
    PCT_80X: float
    PCT_90X: float
    PCT_100X: float
    FOLD_80_BASE_PENALTY: float
    FOLD_90_BASE_PENALTY: float
    FOLD_95_BASE_PENALTY: float
    HET_SNP_SENSITIVITY: float
    HET_SNP_Q: float


class Somalier(BaseModel):
    individual: list[SomalierIndividual]
    comparison: SomalierComparison


class PeddyCheck(BaseModel):
    family_id: str
    paternal_id: float
    maternal_id: float
    sex: float
    phenotype: float
    het_call_rate: float
    het_ratio: float
    het_mean_depth: float
    het_idr_baf: float
    ancestry_prediction: str
    PC1: float
    PC2: float
    PC3: float
    sex_het_ratio: float
    depth_outlier_het_check: bool
    het_count_het_check: float
    het_ratio_het_check: float
    idr_baf_het_check: float
    mean_depth_het_check: float
    median_depth_het_check: float
    p10_het_check: float
    p90_het_check: float
    sampled_sites_het_check: float
    call_rate_het_check: float
    ancestry_prediction_het_check: str
    ancestry_prob_het_check: float
    PC1_het_check: float
    PC2_het_check: float
    PC3_het_check: float
    PC4_het_check: float
    ped_sex_sex_check: str
    hom_ref_count_sex_check: float
    het_count_sex_check: float
    hom_alt_count_sex_check: float
    het_ratio_sex_check: float
    predicted_sex_sex_check: str
    error_sex_check: bool
    ancestry: str


class PicardRNASeqMetrics(BaseModel):
    PF_BASES: float
    PF_ALIGNED_BASES: float
    RIBOSOMAL_BASES: float
    CODING_BASES: float
    UTR_BASES: float
    INTRONIC_BASES: float
    INTERGENIC_BASES: float
    IGNORED_READS: float
    CORRECT_STRAND_READS: float
    INCORRECT_STRAND_READS: float
    NUM_R1_TRANSCRIPT_STRAND_READS: float
    NUM_R2_TRANSCRIPT_STRAND_READS: float
    NUM_UNEXPLAINED_READS: float
    PCT_R1_TRANSCRIPT_STRAND_READS: float
    PCT_R2_TRANSCRIPT_STRAND_READS: float
    PCT_RIBOSOMAL_BASES: float
    PCT_CODING_BASES: float
    PCT_UTR_BASES: float
    PCT_INTRONIC_BASES: float
    PCT_INTERGENIC_BASES: float
    PCT_MRNA_BASES: float
    PCT_USABLE_BASES: float
    PCT_CORRECT_STRAND_READS: float
    MEDIAN_CV_COVERAGE: float
    MEDIAN_5PRIME_BIAS: float
    MEDIAN_3PRIME_BIAS: float
    MEDIAN_5PRIME_TO_3PRIME_BIAS: float
    LIBRARY: str
    READ_GROUP: str
    PF_NOT_ALIGNED_BASES: float


class STARAlignment(BaseModel):
    total_reads: float
    avg_input_read_length: float
    uniquely_mapped: float
    uniquely_mapped_percent: float
    avg_mapped_read_length: float
    num_splices: float
    num_annotated_splices: float
    num_GTAG_splices: float
    num_GCAG_splices: float
    num_ATAC_splices: float
    num_noncanonical_splices: float
    mismatch_rate: float
    deletion_rate: float
    deletion_length: float
    insertion_rate: float
    insertion_length: float
    multimapped: float
    multimapped_percent: float
    multimapped_toomany: float
    multimapped_toomany_percent: float
    unmapped_mismatches_percent: float
    unmapped_tooshort_percent: float
    unmapped_other_percent: float
    unmapped_mismatches: float
    unmapped_tooshort: float
    unmapped_other: float


class RNAfusionGeneralStats(BaseModel):
    INSERT_SIZE_SUM_MEDIAN: float = Field(
        ...,
        alias="Picard_InsertSizeMetrics_mqc_generalstats_picard_insertsizemetrics_summed_median",
    )
    INSERT_SIZE_SUM_MEAN: float = Field(
        ...,
        alias="Picard_InsertSizeMetrics_mqc_generalstats_picard_insertsizemetrics_summed_mean",
    )
    PERCENT_DUPLICATION: float = Field(
        ...,
        alias="Picard_MarkDuplicates_mqc_generalstats_picard_mark_duplicates_PERCENT_DUPLICATION",
    )
    PERCENT_RIBOSOMAL_BASES: float = Field(
        ...,
        alias="Picard_RnaSeqMetrics_mqc_generalstats_picard_rnaseqmetrics_PCT_RIBOSOMAL_BASES",
    )
    PERCENT_MRNA_BASES: float = Field(
        ...,
        alias="Picard_RnaSeqMetrics_mqc_generalstats_picard_rnaseqmetrics_PCT_MRNA_BASES",
    )
    PERCENT_UNIQUELY_MAPPED: float = Field(
        ..., alias="STAR_mqc_generalstats_star_uniquely_mapped_percent"
    )
    UNIQUELY_MAPPED: float = Field(..., alias="STAR_mqc_generalstats_star_uniquely_mapped")
    AFTER_FILTERING_Q30_RATE: float = Field(
        ..., alias="fastp_mqc_generalstats_fastp_after_filtering_q30_rate"
    )
    AFTER_FILTERING_Q30_BASES: float = Field(
        ..., alias="fastp_mqc_generalstats_fastp_after_filtering_q30_bases"
    )
    FILTERING_RESULT_PASSED_FILTER_READS: float = Field(
        ..., alias="fastp_mqc_generalstats_fastp_filtering_result_passed_filter_reads"
    )
    AFTER_FILTERING_GC_CONTENT: float = Field(
        ..., alias="fastp_mqc_generalstats_fastp_after_filtering_gc_content"
    )
    PCT_SURVIVING: float = Field(..., alias="fastp_mqc_generalstats_fastp_pct_surviving")
    PCT_ADAPTER: float = Field(..., alias="fastp_mqc_generalstats_fastp_pct_adapter")
