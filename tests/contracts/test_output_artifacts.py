from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from dqbench.contracts.output_artifacts import (
    CANONICAL_OUTPUT_SCHEMA_REGISTRY,
    MatchArtifact,
    MetricsArtifact,
    SchemaValidationArtifact,
    validate_metrics_artifact,
)
from dqbench.contracts.third_party import (
    ALLOWED_INPUT_ARTIFACTS,
    FORBIDDEN_SIDE_CHANNELS,
    REQUIRED_INPUT_ARTIFACTS,
    REQUIRED_SUBMISSION_ARTIFACTS,
    ThirdPartyDetectorSubmission,
)


def test_canonical_output_schema_registry_covers_required_outputs():
    assert set(CANONICAL_OUTPUT_SCHEMA_REGISTRY) == {
        "alerts",
        "incidents",
        "matches",
        "metrics",
        "schema_validation",
    }
    assert CANONICAL_OUTPUT_SCHEMA_REGISTRY["alerts"]["type"] == "array"
    assert CANONICAL_OUTPUT_SCHEMA_REGISTRY["matches"]["type"] == "object"


def test_match_and_metrics_artifacts_reject_inconsistent_payloads():
    artifact = MatchArtifact(
        matched_pairs=[{"alert_id": "a1", "incident_id": "i1"}],
        duplicate_alert_ids=["a2"],
        unmatched_alert_ids=["a3"],
        missed_incident_ids=["i2"],
    )
    assert artifact.matched_pairs[0].alert_id == "a1"

    with pytest.raises(ValidationError, match="must exclude the primary matched alert ids"):
        MatchArtifact(
            matched_pairs=[{"alert_id": "a1", "incident_id": "i1"}],
            duplicate_alert_ids=["a1"],
        )

    metrics = MetricsArtifact(runtime_overhead_seconds=1.3, incident_precision=0.5)
    assert metrics.runtime_overhead_seconds == 1.3

    with pytest.raises(ValidationError, match="probability-like metrics"):
        validate_metrics_artifact({"runtime_overhead_seconds": 1.0, "incident_precision": 1.5})


def test_schema_validation_artifact_accepts_report_list():
    artifact = SchemaValidationArtifact(
        reports=[
            {
                "artifact_type": "metrics",
                "artifact_path": "outputs/runs/tlc/metrics.json",
                "validator_name": "pandera",
                "passed": True,
                "issues": [],
            }
        ]
    )
    assert artifact.reports[0].artifact_type == "metrics"


def test_third_party_detector_contract_yaml_matches_locked_constants_and_submission_rules():
    path = Path(__file__).resolve().parents[2] / "configs" / "benchmark" / "third_party_detector_contract.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))["third_party_detector_contract"]

    assert tuple(data["allowed_input_artifacts"]) == ALLOWED_INPUT_ARTIFACTS
    assert tuple(data["required_input_artifacts"]) == REQUIRED_INPUT_ARTIFACTS
    assert tuple(data["forbidden_side_channels"]) == FORBIDDEN_SIDE_CHANNELS
    assert tuple(data["required_submission_artifacts"]) == REQUIRED_SUBMISSION_ARTIFACTS

    submission = ThirdPartyDetectorSubmission(
        declaration={
            "detector_id": "external_profile_detector",
            "input_artifacts": ["canonical_batch_profiles", "declared_public_support_tables"],
            "uses_hidden_incident_labels": False,
            "uses_unreleased_snapshots": False,
            "uses_benchmark_private_metadata": False,
            "emits_canonical_alert_schema": True,
            "publishes_configuration_manifest": True,
            "publishes_software_version_manifest": True,
        },
        detector_configuration_manifest={
            "detector_id": "external_profile_detector",
            "detector_family": "external_profile_detector",
            "parameters": {"window": 8},
            "calibration_policies": ["percentile_95"],
        },
        software_version_manifest={
            "detector_id": "external_profile_detector",
            "python_version": "3.11.9",
            "package_versions": {"pandas": "2.0.3"},
        },
        alerts=[
            {
                "alert_id": "a1",
                "run_id": "r1",
                "detector": "external_profile_detector",
                "domain": "tlc",
                "batch_id": "2025-01-01",
                "scope_level": "table",
                "scope_ref": "tlc_trips",
                "score": 4.2,
                "calibration_policy": "percentile_95",
                "payload": {},
            }
        ],
    )
    assert submission.declaration.detector_id == "external_profile_detector"

    with pytest.raises(ValidationError, match="must not access hidden incident labels"):
        ThirdPartyDetectorSubmission(
            declaration={
                "detector_id": "external_profile_detector",
                "input_artifacts": ["canonical_batch_profiles"],
                "uses_hidden_incident_labels": True,
                "emits_canonical_alert_schema": True,
                "publishes_configuration_manifest": True,
                "publishes_software_version_manifest": True,
            },
            detector_configuration_manifest={
                "detector_id": "external_profile_detector",
                "detector_family": "external_profile_detector",
                "parameters": {"window": 8},
                "calibration_policies": ["percentile_95"],
            },
            software_version_manifest={
                "detector_id": "external_profile_detector",
                "python_version": "3.11.9",
                "package_versions": {"pandas": "2.0.3"},
            },
            alerts=[],
        )
