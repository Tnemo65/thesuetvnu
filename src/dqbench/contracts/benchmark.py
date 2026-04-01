"""Locked benchmark constants derived from docs/documentation.md."""

from __future__ import annotations

from typing import Final

CORE_DOMAIN_IDS: Final[tuple[str, ...]] = (
    "tlc",
    "bts",
    "cfpb_consumer_complaints",
    "osha_severe_injury_reports",
    "nyc_hpd_housing_complaints_violations",
    "sec_edgar",
)
EXTERNAL_VALIDATION_DOMAIN_IDS: Final[tuple[str, ...]] = ("nyc311", "austin311")
SUPPLEMENTARY_APPENDIX_IDS: Final[tuple[str, ...]] = ("bts_opsnet_audit_backed_appendix",)

VALID_DOMAINS: Final[tuple[str, ...]] = CORE_DOMAIN_IDS + EXTERNAL_VALIDATION_DOMAIN_IDS
DOMAIN_BATCH_UNITS: Final[dict[str, str]] = {
    "tlc": "daily",
    "bts": "daily",
    "cfpb_consumer_complaints": "daily",
    "osha_severe_injury_reports": "daily",
    "nyc_hpd_housing_complaints_violations": "daily",
    "sec_edgar": "daily",
    "nyc311": "daily",
    "austin311": "daily",
}
VALID_BATCH_UNITS: Final[tuple[str, ...]] = ("daily", "weekly")

VALID_FAULT_FAMILIES: Final[tuple[str, ...]] = (
    "null_spike",
    "range_violation",
    "duplicate_burst",
    "freshness_lag",
    "fk_break",
)
PRIMARY_LEADERBOARD_FAULT_FAMILIES: Final[tuple[str, ...]] = (
    "null_spike",
    "range_violation",
    "duplicate_burst",
    "freshness_lag",
)
VALID_FAULTS: Final[tuple[str, ...]] = VALID_FAULT_FAMILIES + ("clean",)

VALID_SEVERITIES: Final[tuple[str, ...]] = ("low", "medium", "high")
VALID_RUN_SEVERITIES: Final[tuple[str, ...]] = VALID_SEVERITIES + ("none",)
VALID_DURATIONS: Final[tuple[str, ...]] = ("one_window", "sustained")
VALID_RUN_DURATIONS: Final[tuple[str, ...]] = VALID_DURATIONS + ("none",)
SEEDS_PER_CONDITION: Final[int] = 5

LOCKED_BASELINE_DETECTORS: Final[tuple[str, ...]] = (
    "calibration_threshold_lower_bound",
    "constraint_rule_baseline",
    "history_based_robust_profile",
    "ewma_cusum_sequential",
    "isolation_forest",
)
OPTIONAL_REFERENCE_DETECTORS: Final[tuple[str, ...]] = (
    "ecod",
    "copod",
    "extended_isolation_forest",
    "knn",
    "lof",
    "one_class_svm",
)
VALID_DETECTORS: Final[tuple[str, ...]] = LOCKED_BASELINE_DETECTORS + OPTIONAL_REFERENCE_DETECTORS
VALID_CALIBRATIONS: Final[tuple[str, ...]] = ("percentile_90", "percentile_95", "percentile_99")
PRIMARY_CALIBRATION_POLICY: Final[str] = "percentile_95"

PRIMARY_METRICS: Final[tuple[str, ...]] = (
    "incident_recall",
    "incident_precision",
    "incident_f1",
    "detection_delay_norm_mean",
    "localization_accuracy_hierarchical",
    "duplicate_burden",
    "clean_run_fp_batch",
    "runtime_per_1m_rows",
)
SUPPLEMENTARY_METRICS: Final[tuple[str, ...]] = (
    "detection_delay_raw_mean",
    "localization_accuracy_strict",
    "clean_run_fp_alert",
    "runtime_overhead_seconds",
    "weak_label_hit_rate",
    "weak_label_lead_lag_median",
)

VALID_SCOPE_LEVELS: Final[tuple[str, ...]] = ("relation", "table", "column")
FK_BREAK_EXTENSION_DOMAIN_IDS: Final[tuple[str, ...]] = ("tlc", "bts")

RUN_MATRIX: Final[dict[str, object]] = {
    "shared_core_dirty_conditions": 720,
    "fk_break_extension_conditions": 60,
    "clean_evaluation_runs": 6,
    "total_benchmark_runs": 786,
    "locked_baseline_detector_executions": 3930,
    "public_code_reference_detector_executions": 4716,
    "full_empirical_detector_executions": 8646,
    "per_domain": {
        "tlc": {"dirty_runs": 150, "clean_runs": 1},
        "bts": {"dirty_runs": 150, "clean_runs": 1},
        "cfpb_consumer_complaints": {"dirty_runs": 120, "clean_runs": 1},
        "osha_severe_injury_reports": {"dirty_runs": 120, "clean_runs": 1},
        "nyc_hpd_housing_complaints_violations": {"dirty_runs": 120, "clean_runs": 1},
        "sec_edgar": {"dirty_runs": 120, "clean_runs": 1},
    },
}
