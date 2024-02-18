"""Models for the MultiQC intermediate JSON files."""

from pydantic import BaseModel, Field


class PicardDups(BaseModel):
    unpaired_reads_examined: float = Field(..., alias="UNPAIRED_READS_EXAMINED")
    read_pairs_examined: float = Field(..., alias="READ_PAIRS_EXAMINED")
    secondary_or_supplementary_reads: float = Field(..., alias="SECONDARY_OR_SUPPLEMENTARY_RDS")
    unmapped_reads: float = Field(..., alias="UNMAPPED_READS")
    unpaired_read_duplicates: float = Field(..., alias="UNPAIRED_READ_DUPLICATES")
    read_pair_duplicates: float = Field(..., alias="READ_PAIR_DUPLICATES")
    read_pair_optical_duplicates: float = Field(..., alias="READ_PAIR_OPTICAL_DUPLICATES")
    percent_duplication: float = Field(..., alias="PERCENT_DUPLICATION")
    estimated_library_size: float = Field(..., alias="ESTIMATED_LIBRARY_SIZE")


class PicardInsertSize(BaseModel):
    median_insert_size: float = Field(..., alias="MEDIAN_INSERT_SIZE")
    mode_insert_size: float = Field(..., alias="MODE_INSERT_SIZE")
    median_absolute_deviation: float = Field(..., alias="MEDIAN_ABSOLUTE_DEVIATION")
    min_insert_size: float = Field(..., alias="MIN_INSERT_SIZE")
    max_insert_size: float = Field(..., alias="MAX_INSERT_SIZE")
    mean_insert_size: float = Field(..., alias="MEAN_INSERT_SIZE")
    standard_deviation: float = Field(..., alias="STANDARD_DEVIATION")
    read_pairs: float = Field(..., alias="READ_PAIRS")
    pair_orientation: str = Field(..., alias="PAIR_ORIENTATION")
    width_of_10_percent: float = Field(..., alias="WIDTH_OF_10_PERCENT")
    width_of_20_percent: float = Field(..., alias="WIDTH_OF_20_PERCENT")
    width_of_30_percent: float = Field(..., alias="WIDTH_OF_30_PERCENT")
    width_of_40_percent: float = Field(..., alias="WIDTH_OF_40_PERCENT")
    width_of_50_percent: float = Field(..., alias="WIDTH_OF_50_PERCENT")
    width_of_60_percent: float = Field(..., alias="WIDTH_OF_60_PERCENT")
    width_of_70_percent: float = Field(..., alias="WIDTH_OF_70_PERCENT")
    width_of_80_percent: float = Field(..., alias="WIDTH_OF_80_PERCENT")
    width_of_90_percent: float = Field(..., alias="WIDTH_OF_90_PERCENT")
    width_of_95_percent: float = Field(..., alias="WIDTH_OF_95_PERCENT")
    width_of_99_percent: float = Field(..., alias="WIDTH_OF_99_PERCENT")


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
    bait_set: str = Field(..., alias="BAIT_SET")
    bait_territory: float = Field(..., alias="BAIT_TERRITORY")
    bait_design_efficiency: float = Field(..., alias="BAIT_DESIGN_EFFICIENCY")
    on_bait_bases: float = Field(..., alias="ON_BAIT_BASES")
    near_bait_bases: float = Field(..., alias="NEAR_BAIT_BASES")
    off_bait_bases: float = Field(..., alias="OFF_BAIT_BASES")
    pct_selected_bases: float = Field(..., alias="PCT_SELECTED_BASES")
    pct_off_bait: float = Field(..., alias="PCT_OFF_BAIT")
    on_bait_vs_selected: float = Field(..., alias="ON_BAIT_VS_SELECTED")
    mean_bait_coverage: float = Field(..., alias="MEAN_BAIT_COVERAGE")
    pct_usable_bases_on_bait: float = Field(..., alias="PCT_USABLE_BASES_ON_BAIT")
    pct_usable_bases_on_target: float = Field(..., alias="PCT_USABLE_BASES_ON_TARGET")
    fold_enrichment: float = Field(..., alias="FOLD_ENRICHMENT")
    hs_library_size: float = Field(..., alias="HS_LIBRARY_SIZE")
    hs_penalty_10x: float = Field(..., alias="HS_PENALTY_10X")
    hs_penalty_20x: float = Field(..., alias="HS_PENALTY_20X")
    hs_penalty_30x: float = Field(..., alias="HS_PENALTY_30X")
    hs_penalty_40x: float = Field(..., alias="HS_PENALTY_40X")
    hs_penalty_50x: float = Field(..., alias="HS_PENALTY_50X")
    hs_penalty_100x: float = Field(..., alias="HS_PENALTY_100X")
    target_territory: float = Field(..., alias="TARGET_TERRITORY")
    genome_size: float = Field(..., alias="GENOME_SIZE")
    total_reads: float = Field(..., alias="TOTAL_READS")
    pf_reads: float = Field(..., alias="PF_READS")
    pf_bases: float = Field(..., alias="PF_BASES")
    pf_unique_reads: float = Field(..., alias="PF_UNIQUE_READS")
    pf_uq_reads_aligned: float = Field(..., alias="PF_UQ_READS_ALIGNED")
    pf_bases_aligned: float = Field(..., alias="PF_BASES_ALIGNED")
    pf_uq_bases_aligned: float = Field(..., alias="PF_UQ_BASES_ALIGNED")
    on_target_bases: float = Field(..., alias="ON_TARGET_BASES")
    pct_pf_reads: float = Field(..., alias="PCT_PF_READS")
    pct_pf_uq_reads: float = Field(..., alias="PCT_PF_UQ_READS")
    pct_pf_uq_reads_aligned: float = Field(..., alias="PCT_PF_UQ_READS_ALIGNED")
    mean_target_coverage: float = Field(..., alias="MEAN_TARGET_COVERAGE")
    median_target_coverage: float = Field(..., alias="MEDIAN_TARGET_COVERAGE")
    max_target_coverage: float = Field(..., alias="MAX_TARGET_COVERAGE")
    min_target_coverage: float = Field(..., alias="MIN_TARGET_COVERAGE")
    zero_cvg_targets_pct: float = Field(..., alias="ZERO_CVG_TARGETS_PCT")
    pct_exc_dupe: float = Field(..., alias="PCT_EXC_DUPE")
    pct_exc_adapter: float = Field(..., alias="PCT_EXC_ADAPTER")
    pct_exc_mapq: float = Field(..., alias="PCT_EXC_MAPQ")
    pct_exc_baseq: float = Field(..., alias="PCT_EXC_BASEQ")
    pct_exc_overlap: float = Field(..., alias="PCT_EXC_OVERLAP")
    pct_exc_off_target: float = Field(..., alias="PCT_EXC_OFF_TARGET")
    fold_80_base_penalty: float = Field(..., alias="FOLD_80_BASE_PENALTY")
    pct_target_bases_1x: float = Field(..., alias="PCT_TARGET_BASES_1X")
    pct_target_bases_2x: float = Field(..., alias="PCT_TARGET_BASES_2X")
    pct_target_bases_10x: float = Field(..., alias="PCT_TARGET_BASES_10X")
    pct_target_bases_20x: float = Field(..., alias="PCT_TARGET_BASES_20X")
    pct_target_bases_30x: float = Field(..., alias="PCT_TARGET_BASES_30X")
    pct_target_bases_40x: float = Field(..., alias="PCT_TARGET_BASES_40X")
    pct_target_bases_50x: float = Field(..., alias="PCT_TARGET_BASES_50X")
    pct_target_bases_100x: float = Field(..., alias="PCT_TARGET_BASES_100X")
    pct_target_bases_250x: float = Field(..., alias="PCT_TARGET_BASES_250X")
    pct_target_bases_500x: float = Field(..., alias="PCT_TARGET_BASES_500X")
    pct_target_bases_1000x: float = Field(..., alias="PCT_TARGET_BASES_1000X")
    pct_target_bases_2500x: float = Field(..., alias="PCT_TARGET_BASES_2500X")
    pct_target_bases_5000x: float = Field(..., alias="PCT_TARGET_BASES_5000X")
    pct_target_bases_10000x: float = Field(..., alias="PCT_TARGET_BASES_10000X")
    pct_target_bases_25000x: float = Field(..., alias="PCT_TARGET_BASES_25000X")
    pct_target_bases_50000x: float = Field(..., alias="PCT_TARGET_BASES_50000X")
    pct_target_bases_100000x: float = Field(..., alias="PCT_TARGET_BASES_100000X")
    at_dropout: float = Field(..., alias="AT_DROPOUT")
    gc_dropout: float = Field(..., alias="GC_DROPOUT")
    het_snp_sensitivity: float = Field(..., alias="HET_SNP_SENSITIVITY")
    het_snp_q: float = Field(..., alias="HET_SNP_Q")


class PicardAlignmentSummary(BaseModel):
    category: str = Field(..., alias="CATEGORY")
    total_reads: float = Field(..., alias="TOTAL_READS")
    pf_reads: float = Field(..., alias="PF_READS")
    pct_pf_reads: float = Field(..., alias="PCT_PF_READS")
    pf_noise_reads: float = Field(..., alias="PF_NOISE_READS")
    pf_reads_aligned: float = Field(..., alias="PF_READS_ALIGNED")
    pct_pf_reads_aligned: float = Field(..., alias="PCT_PF_READS_ALIGNED")
    pf_aligned_bases: float = Field(..., alias="PF_ALIGNED_BASES")
    pf_hq_aligned_reads: float = Field(..., alias="PF_HQ_ALIGNED_READS")
    pf_hq_aligned_bases: float = Field(..., alias="PF_HQ_ALIGNED_BASES")
    pf_hq_aligned_q20_bases: float = Field(..., alias="PF_HQ_ALIGNED_Q20_BASES")
    pf_hq_median_mismatches: float = Field(..., alias="PF_HQ_MEDIAN_MISMATCHES")
    pf_mismatch_rate: float = Field(..., alias="PF_MISMATCH_RATE")
    pf_hq_error_rate: float = Field(..., alias="PF_HQ_ERROR_RATE")
    pf_indel_rate: float = Field(..., alias="PF_INDEL_RATE")
    mean_read_length: float = Field(..., alias="MEAN_READ_LENGTH")
    sd_read_length: float = Field(..., alias="SD_READ_LENGTH")
    median_read_length: float = Field(..., alias="MEDIAN_READ_LENGTH")
    mad_read_length: float = Field(..., alias="MAD_READ_LENGTH")
    min_read_length: float = Field(..., alias="MIN_READ_LENGTH")
    max_read_length: float = Field(..., alias="MAX_READ_LENGTH")
    reads_aligned_in_pairs: float = Field(..., alias="READS_ALIGNED_IN_PAIRS")
    pct_reads_aligned_in_pairs: float = Field(..., alias="PCT_READS_ALIGNED_IN_PAIRS")
    pf_reads_improper_pairs: float = Field(..., alias="PF_READS_IMPROPER_PAIRS")
    pct_pf_reads_improper_pairs: float = Field(..., alias="PCT_PF_READS_IMPROPER_PAIRS")
    bad_cycles: float = Field(..., alias="BAD_CYCLES")
    strand_balance: float = Field(..., alias="STRAND_BALANCE")
    pct_chimeras: float = Field(..., alias="PCT_CHIMERAS")
    pct_adapter: float = Field(..., alias="PCT_ADAPTER")
    pct_softclip: float = Field(..., alias="PCT_SOFTCLIP")
    pct_hardclip: float = Field(..., alias="PCT_HARDCLIP")
    avg_pos_3prime_softclip_length: float = Field(..., alias="AVG_POS_3PRIME_SOFTCLIP_LENGTH")


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
    genome_territory: float = Field(..., alias="GENOME_TERRITORY")
    mean_coverage: float = Field(..., alias="MEAN_COVERAGE")
    sd_coverage: float = Field(..., alias="SD_COVERAGE")
    median_coverage: float = Field(..., alias="MEDIAN_COVERAGE")
    mad_coverage: float = Field(..., alias="MAD_COVERAGE")
    pct_exc_adapter: float = Field(..., alias="PCT_EXC_ADAPTER")
    pct_exc_mapq: float = Field(..., alias="PCT_EXC_MAPQ")
    pct_exc_dupe: float = Field(..., alias="PCT_EXC_DUPE")
    pct_exc_unpaired: float = Field(..., alias="PCT_EXC_UNPAIRED")
    pct_exc_baseq: float = Field(..., alias="PCT_EXC_BASEQ")
    pct_exc_overlap: float = Field(..., alias="PCT_EXC_OVERLAP")
    pct_exc_capped: float = Field(..., alias="PCT_EXC_CAPPED")
    pct_exc_total: float = Field(..., alias="PCT_EXC_TOTAL")
    pct_1x: float = Field(..., alias="PCT_1X")
    pct_5x: float = Field(..., alias="PCT_5X")
    pct_10x: float = Field(..., alias="PCT_10X")
    pct_15x: float = Field(..., alias="PCT_15X")
    pct_20x: float = Field(..., alias="PCT_20X")
    pct_25x: float = Field(..., alias="PCT_25X")
    pct_30x: float = Field(..., alias="PCT_30X")
    pct_40x: float = Field(..., alias="PCT_40X")
    pct_50x: float = Field(..., alias="PCT_50X")
    pct_60x: float = Field(..., alias="PCT_60X")
    pct_70x: float = Field(..., alias="PCT_70X")
    pct_80x: float = Field(..., alias="PCT_80X")
    pct_90x: float = Field(..., alias="PCT_90X")
    pct_100x: float = Field(..., alias="PCT_100X")
    fold_80_base_penalty: float = Field(..., alias="FOLD_80_BASE_PENALTY")
    fold_90_base_penalty: float = Field(..., alias="FOLD_90_BASE_PENALTY")
    fold_95_base_penalty: float = Field(..., alias="FOLD_95_BASE_PENALTY")
    het_snp_sensitivity: float = Field(..., alias="HET_SNP_SENSITIVITY")
    het_snp_q: float = Field(..., alias="HET_SNP_Q")


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
    pf_bases: float = Field(..., alias="PF_BASES")
    pf_aligned_bases: float = Field(..., alias="PF_ALIGNED_BASES")
    ribosomal_bases: float = Field(..., alias="RIBOSOMAL_BASES")
    coding_bases: float = Field(..., alias="CODING_BASES")
    utr_bases: float = Field(..., alias="UTR_BASES")
    intronic_bases: float = Field(..., alias="INTRONIC_BASES")
    intergenic_bases: float = Field(..., alias="INTERGENIC_BASES")
    ignored_reads: float = Field(..., alias="IGNORED_READS")
    correct_strand_reads: float = Field(..., alias="CORRECT_STRAND_READS")
    incorrect_strand_reads: float = Field(..., alias="INCORRECT_STRAND_READS")
    num_r1_transcript_strand_reads: float = Field(..., alias="NUM_R1_TRANSCRIPT_STRAND_READS")
    num_r2_transcript_strand_reads: float = Field(..., alias="NUM_R2_TRANSCRIPT_STRAND_READS")
    num_unexplained_reads: float = Field(..., alias="NUM_UNEXPLAINED_READS")
    pct_r1_transcript_strand_reads: float = Field(..., alias="PCT_R1_TRANSCRIPT_STRAND_READS")
    pct_r2_transcript_strand_reads: float = Field(..., alias="PCT_R2_TRANSCRIPT_STRAND_READS")
    pct_ribosomal_bases: float = Field(..., alias="PCT_RIBOSOMAL_BASES")
    pct_coding_bases: float = Field(..., alias="PCT_CODING_BASES")
    pct_utr_bases: float = Field(..., alias="PCT_UTR_BASES")
    pct_intronic_bases: float = Field(..., alias="PCT_INTRONIC_BASES")
    pct_intergenic_bases: float = Field(..., alias="PCT_INTERGENIC_BASES")
    pct_mrna_bases: float = Field(..., alias="PCT_MRNA_BASES")
    pct_usable_bases: float = Field(..., alias="PCT_USABLE_BASES")
    pct_correct_strand_reads: float = Field(..., alias="PCT_CORRECT_STRAND_READS")
    median_cv_coverage: float = Field(..., alias="MEDIAN_CV_COVERAGE")
    median_5prime_bias: float = Field(..., alias="MEDIAN_5PRIME_BIAS")
    median_3prime_bias: float = Field(..., alias="MEDIAN_3PRIME_BIAS")
    median_5prime_to_3prime_bias: float = Field(..., alias="MEDIAN_5PRIME_TO_3PRIME_BIAS")
    library: str = Field(..., alias="LIBRARY")
    read_group: str = Field(..., alias="READ_GROUP")
    pf_not_aligned_bases: float = Field(..., alias="PF_NOT_ALIGNED_BASES")


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
    insert_size_sum_median: float = Field(
        ...,
        alias="Picard_InsertSizeMetrics_mqc_generalstats_picard_insertsizemetrics_summed_median",
    )
    insert_size_sum_mean: float = Field(
        ..., alias="Picard_InsertSizeMetrics_mqc_generalstats_picard_insertsizemetrics_summed_mean"
    )
    percent_duplication: float = Field(
        ...,
        alias="Picard_MarkDuplicates_mqc_generalstats_picard_mark_duplicates_PERCENT_DUPLICATION",
    )
    percent_ribosomal_bases: float = Field(
        ..., alias="Picard_RnaSeqMetrics_mqc_generalstats_picard_rnaseqmetrics_PCT_RIBOSOMAL_BASES"
    )
    percent_mrna_bases: float = Field(
        ..., alias="Picard_RnaSeqMetrics_mqc_generalstats_picard_rnaseqmetrics_PCT_MRNA_BASES"
    )
    percent_uniquely_mapped: float = Field(
        ..., alias="STAR_mqc_generalstats_star_uniquely_mapped_percent"
    )
    uniquely_mapped: float = Field(..., alias="STAR_mqc_generalstats_star_uniquely_mapped")
    after_filtering_q30_rate: float = Field(
        ..., alias="fastp_mqc_generalstats_fastp_after_filtering_q30_rate"
    )
    after_filtering_q30_bases: float = Field(
        ..., alias="fastp_mqc_generalstats_fastp_after_filtering_q30_bases"
    )
    filtering_result_passed_filter_reads: float = Field(
        ..., alias="fastp_mqc_generalstats_fastp_filtering_result_passed_filter_reads"
    )
    after_filtering_gc_content: float = Field(
        ..., alias="fastp_mqc_generalstats_fastp_after_filtering_gc_content"
    )
    pct_surviving: float = Field(..., alias="fastp_mqc_generalstats_fastp_pct_surviving")
    pct_adapter: float = Field(..., alias="fastp_mqc_generalstats_fastp_pct_adapter")
