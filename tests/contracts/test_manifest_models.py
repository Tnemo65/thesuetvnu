import pytest
from pydantic import ValidationError

from dqbench.contracts.manifests import (
    CalibrationCleanlinessReport,
    DetectorConfigurationManifest,
    InjectionManifest,
    MonitoredScopeCatalog,
    RuntimeManifest,
    SchemaValidationReport,
    SnapshotManifest,
)


def test_snapshot_manifest_requires_consistent_snapshot_identity_and_valid_checksum():
    manifest = SnapshotManifest(
        entries=[
            {
                "dataset_id": "tlc",
                "snapshot_id": "2025-01",
                "snapshot_date": "2025-01-31",
                "source_reference": "https://example.com/tlc",
                "local_path": "data/raw/tlc/file1.parquet",
                "schema_version_reference": "yellow-v1",
                "checksum_sha256": "a" * 64,
                "file_role": "raw_file",
            },
            {
                "dataset_id": "tlc",
                "snapshot_id": "2025-01",
                "snapshot_date": "2025-01-31",
                "source_reference": "https://example.com/tlc-zone",
                "local_path": "data/raw/tlc/file2.csv",
                "schema_version_reference": "yellow-v1",
                "checksum_sha256": "b" * 64,
                "file_role": "support_table",
            },
        ]
    )

    assert len(manifest.entries) == 2

    with pytest.raises(ValidationError, match="checksum_sha256"):
        SnapshotManifest(
            entries=[
                {
                    "dataset_id": "tlc",
                    "snapshot_id": "2025-01",
                    "snapshot_date": "2025-01-31",
                    "source_reference": "https://example.com/tlc",
                    "local_path": "data/raw/tlc/file1.parquet",
                    "schema_version_reference": "yellow-v1",
                    "checksum_sha256": "XYZ",
                }
            ]
        )


def test_monitored_scope_catalog_requires_fault_frame_coverage_for_all_locked_families():
    valid_catalog = MonitoredScopeCatalog(
        domain_id="tlc",
        monitored_completeness_columns=["fare_amount"],
        monitored_numeric_validity_columns=[
            {"column": "fare_amount", "valid_range_source": "official data dictionary", "min_value": 0.0, "max_value": 500.0}
        ],
        duplicate_policy={"key_columns": ["VendorID", "batch_id"]},
        monitored_foreign_key_columns=[{"column": "PULocationID", "support_table": "taxi_zone_lookup", "reference_column": "LocationID"}],
        declared_public_support_tables=[{"table_id": "taxi_zone_lookup", "join_key": "LocationID"}],
        batch_schedule_policy="daily batches",
        calendar_construction_policy="closed daily calendar including zero-row scheduled batches",
        admissible_target_scope_sampling_frames=[
            {"fault_family": "null_spike", "enabled": True, "scope_level": "column", "candidate_scope_refs": ["tlc_trips.fare_amount"], "selection_policy": "uniform over monitored completeness columns"},
            {"fault_family": "range_violation", "enabled": True, "scope_level": "column", "candidate_scope_refs": ["tlc_trips.fare_amount"], "selection_policy": "uniform over monitored numeric validity columns"},
            {"fault_family": "duplicate_burst", "enabled": True, "scope_level": "table", "candidate_scope_refs": ["tlc_trips"], "selection_policy": "table fixed"},
            {"fault_family": "freshness_lag", "enabled": True, "scope_level": "table", "candidate_scope_refs": ["tlc_trips"], "selection_policy": "table fixed"},
            {"fault_family": "fk_break", "enabled": True, "scope_level": "column", "candidate_scope_refs": ["tlc_trips.PULocationID"], "selection_policy": "uniform over monitored foreign keys"},
        ],
    )

    assert valid_catalog.domain_id == "tlc"

    with pytest.raises(ValidationError, match="coverage for every locked fault family"):
        MonitoredScopeCatalog(
            domain_id="tlc",
            monitored_completeness_columns=["fare_amount"],
            duplicate_policy={"definition": "row duplicates by business key"},
            batch_schedule_policy="daily batches",
            calendar_construction_policy="closed daily calendar including zero-row scheduled batches",
            admissible_target_scope_sampling_frames=[
                {"fault_family": "null_spike", "enabled": True, "scope_level": "column", "candidate_scope_refs": ["tlc_trips.fare_amount"], "selection_policy": "uniform"}
            ],
        )


def test_calibration_cleanliness_report_rejects_impossible_final_counts():
    report = CalibrationCleanlinessReport(
        domain_id="bts",
        snapshot_id="2025-01",
        candidate_calibration_range={"start_batch": "2025-01-01", "end_batch": "2025-01-30", "batch_count": 30},
        removed_failures=[{"batch_id": "2025-01-05", "failure_type": "schema_failure", "description": "missing required column"}],
        excluded_batches=["2025-01-05"],
        deterministic_exclusion_rule="exclude batches with schema or support-table validation failures",
        final_screened_clean_calibration_batches=29,
    )

    assert report.final_screened_clean_calibration_batches == 29

    with pytest.raises(ValidationError, match="cannot exceed candidate batch_count"):
        CalibrationCleanlinessReport(
            domain_id="bts",
            snapshot_id="2025-01",
            candidate_calibration_range={"start_batch": "2025-01-01", "end_batch": "2025-01-30", "batch_count": 30},
            deterministic_exclusion_rule="exclude invalid batches",
            final_screened_clean_calibration_batches=31,
        )


def test_detector_configuration_manifest_requires_json_like_parameters():
    manifest = DetectorConfigurationManifest(
        detector_id="ewma_cusum_sequential",
        detector_family="sequential_change_monitoring",
        parameters={"ewma_lambda": 0.3, "cusum_k": 0.5, "scopes": ["table", "column"]},
        calibration_policies=["percentile_95"],
    )

    assert manifest.parameters["ewma_lambda"] == 0.3

    with pytest.raises(ValidationError, match="JSON-like"):
        DetectorConfigurationManifest(
            detector_id="ewma_cusum_sequential",
            detector_family="sequential_change_monitoring",
            parameters={"bad": {1, 2, 3}},
            calibration_policies=["percentile_95"],
        )


def test_injection_manifest_handles_general_and_freshness_specific_contracts():
    manifest = InjectionManifest(
        domain_id="tlc",
        fault_family="null_spike",
        injection_operator_family="column_nulling",
        parameter_ranges={"severity_map": {"low": 0.1, "medium": 0.25, "high": 0.5}},
        seed_semantics="seed chooses target batches and affected rows deterministically",
        edit_budget_or_batch_manipulation_policy="edit up to the configured row fraction inside the target batches",
        plausibility_guards_on_non_target_features=["do not edit columns outside the target completeness column"],
        target_scope_selection_policy="uniform over monitored completeness columns",
    )

    assert manifest.fault_family == "null_spike"

    freshness_manifest = InjectionManifest(
        domain_id="tlc",
        fault_family="freshness_lag",
        injection_operator_family="missing_batch_omission",
        parameter_ranges={"delay_days_map": {"low": 1, "medium": 2, "high": 3}},
        seed_semantics="seed chooses target batches deterministically",
        edit_budget_or_batch_manipulation_policy="omit or delay only the selected scheduled batches",
        plausibility_guards_on_non_target_features=["leave non-target batches untouched"],
        target_scope_selection_policy="fixed table-level scope",
        lag_implementation="omitted batch materialization",
    )

    assert freshness_manifest.lag_implementation == "omitted_batch_materialization"

    with pytest.raises(ValidationError, match="must declare lag_implementation"):
        InjectionManifest(
            domain_id="tlc",
            fault_family="freshness_lag",
            injection_operator_family="missing_batch_omission",
            parameter_ranges={"delay_days_map": {"low": 1, "medium": 2, "high": 3}},
            seed_semantics="seed chooses target batches deterministically",
            edit_budget_or_batch_manipulation_policy="omit or delay only the selected scheduled batches",
            plausibility_guards_on_non_target_features=["leave non-target batches untouched"],
            target_scope_selection_policy="fixed table-level scope",
        )


def test_runtime_manifest_requires_non_empty_policy_and_environment_fields():
    manifest = RuntimeManifest(
        runtime_boundary="detector fit + score + alert emission on canonical batch profiles",
        hardware_specification={"cpu": "8-core", "memory_gb": 32},
        thread_count_policy="single-threaded detector execution unless explicitly documented",
        cache_policy="cold filesystem cache before timed runs",
        environment={"python_version": "3.8.20", "packages": {"pandas": "2.0.3"}},
    )

    assert manifest.hardware_specification["cpu"] == "8-core"

    with pytest.raises(ValidationError, match="must not be empty"):
        RuntimeManifest(
            runtime_boundary="detector fit + score + alert emission on canonical batch profiles",
            hardware_specification={},
            thread_count_policy="single-threaded detector execution unless explicitly documented",
            cache_policy="cold filesystem cache before timed runs",
            environment={"python_version": "3.8.20"},
        )


def test_schema_validation_report_tracks_pass_fail_consistently():
    report = SchemaValidationReport(
        artifact_type="metrics",
        artifact_path="outputs/runs/tlc/metrics.json",
        validator_name="pydantic",
        passed=False,
        issues=[{"location": "runtime_per_1m_rows", "message": "missing value", "severity": "error"}],
    )

    assert report.passed is False

    with pytest.raises(ValidationError, match="cannot include error issues"):
        SchemaValidationReport(
            artifact_type="metrics",
            artifact_path="outputs/runs/tlc/metrics.json",
            validator_name="pydantic",
            passed=True,
            issues=[{"location": "runtime_per_1m_rows", "message": "missing value", "severity": "error"}],
        )
