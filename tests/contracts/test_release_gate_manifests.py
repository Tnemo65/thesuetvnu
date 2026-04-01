from pathlib import Path

import yaml


RELEASE_GATE_IDS = (
    "locked_design_no_scope_drift",
    "core_domains_executed",
    "released_datasets_pass_domain_inclusion_gate",
    "shared_core_leaderboard_reported",
    "fk_break_extension_reported_for_qualifying_domains",
    "locked_baseline_families_executed",
    "public_code_reference_detectors_executed",
    "primary_metrics_reported_per_condition",
    "clean_run_false_positive_evaluation_included",
    "monitored_scope_and_injection_artifacts_published",
    "operator_evidence_and_robustness_outputs_published",
    "audited_clean_track_published",
    "runtime_boundary_and_hardware_policy_published",
    "threshold_sensitivity_appendix_published",
    "detector_configuration_manifests_frozen",
    "inferential_statistics_reported",
    "nyc311_external_validation_published",
    "austin311_external_validation_published",
    "bts_audit_backed_appendix_published",
    "transfer_analysis_outputs_published",
    "public_code_reference_appendix_published",
    "native_multi_alert_appendix_published_if_applicable",
    "strict_schema_validation_passes",
    "reproducible_artifact_bundle_published",
)

SNAPSHOT_POLICY_FIELDS = (
    "dataset_identifier",
    "snapshot_identifier",
    "snapshot_date",
    "source_reference",
    "schema_version_reference",
    "raw_file_checksums",
    "support_table_checksums",
)

PUBLIC_RELEASE_ARTIFACTS = (
    "benchmark_source_code",
    "executable_condition_configs",
    "seed_lists",
    "data_acquisition_scripts",
    "monitored_scope_catalogs",
    "injection_manifests",
    "realized_severity_manifests",
    "operator_evidence_maps",
    "calibration_cleanliness_reports",
    "audited_clean_track_protocol_and_audit_outputs",
    "strict_pydantic_models",
    "pandera_schemas",
    "manifests_and_checksums",
    "frozen_split_definitions",
    "containerized_runtime_environment",
    "one_command_pilot_entry_point",
    "one_command_full_suite_entry_point",
    "runtime_measurement_policy_and_hardware_manifest",
    "detector_adapter_template",
    "output_schema_validator",
    "machine_readable_schema_validation_reports",
    "canonical_output_schemas",
    "aggregate_tables_used_in_paper",
    "transfer_analysis_tables_and_summaries",
    "domain_scale_disclosure_tables",
    "detector_native_multi_alert_appendix_outputs",
)

PER_RUN_OUTPUTS = ("alerts", "incidents", "matches", "metrics", "schema_validation")
DETECTOR_SUBMISSION_OUTPUTS = (
    "detector_configuration_manifest",
    "software_version_manifest",
    "runtime_environment_manifest",
    "detector_native_alert_appendix_outputs_when_applicable",
)
PAPER_SCALE_RELEASE_OUTPUTS = (
    "per_domain_summary_tables",
    "shared_core_cross_domain_leaderboard_tables",
    "fk_break_extension_tables",
    "nyc311_external_validation_case_study_outputs",
    "austin311_external_validation_case_study_outputs",
    "bts_audit_backed_supplementary_validation_outputs",
    "audited_clean_track_outputs",
    "transfer_analysis_outputs",
    "domain_scale_disclosure_outputs",
)
NON_REDISTRIBUTABLE_SOURCE_OUTPUTS = (
    "acquisition_procedure",
    "exact_source_references",
    "checksums",
    "expected_local_directory_structure",
)


def _load_yaml(relative_path: str) -> dict:
    repo_root = Path(__file__).resolve().parents[2]
    path = repo_root / relative_path
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_release_gate_manifest_freezes_all_paper_scale_requirements():
    data = _load_yaml("configs/benchmark/release_gate.yaml")
    requirements = data["release_gate"]["requirements"]

    assert data["release_gate"]["release_class"] == "paper_scale"
    assert tuple(item["id"] for item in requirements) == RELEASE_GATE_IDS
    assert {item["check_type"] for item in requirements} == {"boolean", "integer_equals"}
    assert all(item["scope"] in {"release", "benchmark_condition"} for item in requirements)


def test_artifact_requirement_manifest_matches_spec_sections():
    data = _load_yaml("configs/benchmark/artifact_requirements.yaml")["artifact_requirements"]

    assert tuple(data["snapshot_policy"]["required_fields"]) == SNAPSHOT_POLICY_FIELDS
    assert tuple(data["public_release_contents"]["required_artifacts"]) == PUBLIC_RELEASE_ARTIFACTS
    assert tuple(data["per_run_outputs"]["required_outputs"]) == PER_RUN_OUTPUTS
    assert tuple(data["detector_submission"]["required_outputs"]) == DETECTOR_SUBMISSION_OUTPUTS
    assert tuple(data["paper_scale_release_outputs"]["required_outputs"]) == PAPER_SCALE_RELEASE_OUTPUTS
    assert tuple(data["raw_data_policy"]["non_redistributable_source"]["required_outputs"]) == NON_REDISTRIBUTABLE_SOURCE_OUTPUTS
    assert data["raw_data_policy"]["redistributable_source"]["required_outputs"] == [
        "raw_files_packaged_per_source_policy"
    ]
