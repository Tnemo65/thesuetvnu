"""Third-party detector submission contract."""

from __future__ import annotations

from typing import Any, Dict, List

from pydantic import Field, root_validator, validator

from dqbench.contracts.manifests import (
    DetectorConfigurationManifest,
    SoftwareVersionManifest,
    StrictModel,
    _ensure_non_empty_string,
)
from dqbench.contracts.output_artifacts import AlertArtifactRecord

ALLOWED_INPUT_ARTIFACTS = ("canonical_batch_profiles", "declared_public_support_tables")
REQUIRED_INPUT_ARTIFACTS = ("canonical_batch_profiles",)
FORBIDDEN_SIDE_CHANNELS = (
    "hidden_incident_labels",
    "unreleased_snapshots",
    "benchmark_private_metadata",
)
REQUIRED_SUBMISSION_ARTIFACTS = (
    "canonical_alert_schema",
    "detector_configuration_manifest",
    "software_version_manifest",
)


class ThirdPartyDetectorDeclaration(StrictModel):
    detector_id: str
    input_artifacts: List[str] = Field(..., min_items=1)
    uses_hidden_incident_labels: bool = False
    uses_unreleased_snapshots: bool = False
    uses_benchmark_private_metadata: bool = False
    emits_canonical_alert_schema: bool = True
    publishes_configuration_manifest: bool = True
    publishes_software_version_manifest: bool = True

    @validator("detector_id")
    def _validate_detector_id(cls, value: str) -> str:
        return _ensure_non_empty_string("detector_id", value)

    @validator("input_artifacts", each_item=True)
    def _validate_input_artifact(cls, value: str) -> str:
        value = _ensure_non_empty_string("input_artifacts", value)
        if value not in ALLOWED_INPUT_ARTIFACTS:
            raise ValueError(f"input_artifacts must be drawn from {ALLOWED_INPUT_ARTIFACTS}")
        return value

    @root_validator
    def _validate_locked_contract(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        input_artifacts = values.get("input_artifacts") or []
        if "canonical_batch_profiles" not in input_artifacts:
            raise ValueError("third-party detectors must consume canonical_batch_profiles")
        if values.get("uses_hidden_incident_labels"):
            raise ValueError("third-party detectors must not access hidden incident labels")
        if values.get("uses_unreleased_snapshots"):
            raise ValueError("third-party detectors must not access unreleased snapshots")
        if values.get("uses_benchmark_private_metadata"):
            raise ValueError("third-party detectors must not access benchmark-private metadata")
        if not values.get("emits_canonical_alert_schema"):
            raise ValueError("third-party detectors must emit the canonical alert schema")
        if not values.get("publishes_configuration_manifest"):
            raise ValueError("third-party detectors must publish a configuration manifest")
        if not values.get("publishes_software_version_manifest"):
            raise ValueError("third-party detectors must publish a software version manifest")
        return values


class ThirdPartyDetectorSubmission(StrictModel):
    declaration: ThirdPartyDetectorDeclaration
    detector_configuration_manifest: DetectorConfigurationManifest
    software_version_manifest: SoftwareVersionManifest
    alerts: List[AlertArtifactRecord] = Field(default_factory=list)

    @root_validator
    def _validate_submission_alignment(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        declaration = values.get("declaration")
        config_manifest = values.get("detector_configuration_manifest")
        software_version_manifest = values.get("software_version_manifest")
        alerts = values.get("alerts") or []
        if declaration is None or config_manifest is None or software_version_manifest is None:
            return values

        if config_manifest.detector_id != declaration.detector_id:
            raise ValueError("detector_configuration_manifest.detector_id must match declaration.detector_id")
        if software_version_manifest.detector_id != declaration.detector_id:
            raise ValueError("software_version_manifest.detector_id must match declaration.detector_id")
        for alert in alerts:
            if alert.detector != declaration.detector_id:
                raise ValueError("every submitted alert must use the declared detector_id")
        return values
