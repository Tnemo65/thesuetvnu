from pathlib import Path

import yaml

from dqbench.contracts.benchmark import (
    CORE_DOMAIN_IDS,
    EXTERNAL_VALIDATION_DOMAIN_IDS,
    FK_BREAK_EXTENSION_DOMAIN_IDS,
    LOCKED_BASELINE_DETECTORS,
    OPTIONAL_REFERENCE_DETECTORS,
    PRIMARY_CALIBRATION_POLICY,
    PRIMARY_LEADERBOARD_FAULT_FAMILIES,
    PRIMARY_METRICS,
    RUN_MATRIX,
    SEEDS_PER_CONDITION,
    SUPPLEMENTARY_APPENDIX_IDS,
    VALID_CALIBRATIONS,
    VALID_DURATIONS,
    VALID_FAULT_FAMILIES,
    VALID_SEVERITIES,
)


def test_benchmark_constants_manifest_matches_locked_python_constants():
    manifest_path = Path(__file__).resolve().parents[2] / "configs" / "benchmark" / "constants.yaml"
    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    benchmark = data["benchmark"]

    assert tuple(item["id"] for item in benchmark["domains"]["core"]) == CORE_DOMAIN_IDS
    assert tuple(item["id"] for item in benchmark["domains"]["external_validation"]) == EXTERNAL_VALIDATION_DOMAIN_IDS
    assert tuple(item["id"] for item in benchmark["supplementary_appendices"]) == SUPPLEMENTARY_APPENDIX_IDS

    assert tuple(benchmark["fault_families"]) == VALID_FAULT_FAMILIES
    assert tuple(benchmark["primary_leaderboard_fault_families"]) == PRIMARY_LEADERBOARD_FAULT_FAMILIES
    assert tuple(benchmark["detectors"]["locked_baselines"]) == LOCKED_BASELINE_DETECTORS
    assert tuple(item["id"] for item in benchmark["detectors"]["optional_reference"]) == OPTIONAL_REFERENCE_DETECTORS
    assert tuple(benchmark["primary_metrics"]) == PRIMARY_METRICS
    assert tuple(benchmark["condition_axes"]["severities"]) == VALID_SEVERITIES
    assert tuple(benchmark["condition_axes"]["durations"]) == VALID_DURATIONS
    assert benchmark["condition_axes"]["seeds_per_condition"] == SEEDS_PER_CONDITION
    assert benchmark["calibration"]["primary_leaderboard_policy"] == PRIMARY_CALIBRATION_POLICY
    assert tuple(benchmark["calibration"]["threshold_sensitivity_policies"]) == VALID_CALIBRATIONS
    assert tuple(benchmark["run_matrix"]["fk_break_extension_domains"]) == FK_BREAK_EXTENSION_DOMAIN_IDS


def test_run_matrix_is_locked_to_spec_counts():
    per_domain = RUN_MATRIX["per_domain"]

    assert per_domain["tlc"] == {"dirty_runs": 150, "clean_runs": 1}
    assert per_domain["bts"] == {"dirty_runs": 150, "clean_runs": 1}
    assert per_domain["cfpb_consumer_complaints"] == {"dirty_runs": 120, "clean_runs": 1}
    assert per_domain["osha_severe_injury_reports"] == {"dirty_runs": 120, "clean_runs": 1}
    assert per_domain["nyc_hpd_housing_complaints_violations"] == {"dirty_runs": 120, "clean_runs": 1}
    assert per_domain["sec_edgar"] == {"dirty_runs": 120, "clean_runs": 1}

    total_runs = sum(item["dirty_runs"] + item["clean_runs"] for item in per_domain.values())
    assert RUN_MATRIX["shared_core_dirty_conditions"] == 720
    assert RUN_MATRIX["fk_break_extension_conditions"] == 60
    assert RUN_MATRIX["clean_evaluation_runs"] == 6
    assert RUN_MATRIX["total_benchmark_runs"] == total_runs == 786
    assert RUN_MATRIX["locked_baseline_detector_executions"] == total_runs * len(LOCKED_BASELINE_DETECTORS) == 3930
    assert RUN_MATRIX["public_code_reference_detector_executions"] == total_runs * len(OPTIONAL_REFERENCE_DETECTORS) == 4716
    assert RUN_MATRIX["full_empirical_detector_executions"] == total_runs * (
        len(LOCKED_BASELINE_DETECTORS) + len(OPTIONAL_REFERENCE_DETECTORS)
    ) == 8646
