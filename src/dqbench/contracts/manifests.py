"""Strict Pydantic models for benchmark manifests and reports."""

from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, root_validator, validator

from dqbench.contracts.benchmark import VALID_DOMAINS, VALID_FAULT_FAMILIES


def _ensure_non_empty_string(name: str, value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value.strip()


def _validate_json_like(value: Any, path: str) -> None:
    if value is None:
        return
    if isinstance(value, (str, bool, int, float)):
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _validate_json_like(item, f"{path}[{index}]")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str) or not key.strip():
                raise ValueError(f"{path} must use non-empty string keys")
            _validate_json_like(item, f"{path}.{key}")
        return
    raise ValueError(f"{path} must contain only JSON-like scalar, list, or mapping values")


class StrictModel(BaseModel):
    class Config:
        extra = "forbid"
        anystr_strip_whitespace = True
        validate_assignment = True
        allow_mutation = False


class SnapshotManifestEntry(StrictModel):
    dataset_id: str
    snapshot_id: str
    snapshot_date: date
    source_reference: str
    local_path: str
    schema_version_reference: str
    checksum_sha256: str
    file_role: str = "raw_file"

    @validator("dataset_id", "snapshot_id", "source_reference", "local_path", "schema_version_reference")
    def _validate_text_fields(cls, value: str, field: Any) -> str:
        return _ensure_non_empty_string(field.name, value)

    @validator("file_role")
    def _validate_file_role(cls, value: str) -> str:
        value = _ensure_non_empty_string("file_role", value)
        if value not in {"raw_file", "support_table"}:
            raise ValueError("file_role must be 'raw_file' or 'support_table'")
        return value

    @validator("checksum_sha256")
    def _validate_checksum(cls, value: str) -> str:
        value = _ensure_non_empty_string("checksum_sha256", value)
        if len(value) != 64 or any(ch not in "0123456789abcdef" for ch in value):
            raise ValueError("checksum_sha256 must be a 64-character lowercase hex digest")
        return value


class SnapshotManifest(StrictModel):
    entries: List[SnapshotManifestEntry] = Field(..., min_items=1)

    @root_validator
    def _validate_shared_snapshot_identity(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        entries = values.get("entries") or []
        if not entries:
            raise ValueError("entries must contain at least one snapshot file record")

        first = entries[0]
        shared_identity = (
            first.dataset_id,
            first.snapshot_id,
            first.snapshot_date,
            first.schema_version_reference,
        )
        for entry in entries[1:]:
            current_identity = (
                entry.dataset_id,
                entry.snapshot_id,
                entry.snapshot_date,
                entry.schema_version_reference,
            )
            if current_identity != shared_identity:
                raise ValueError("all snapshot entries must share dataset_id, snapshot_id, snapshot_date, and schema_version_reference")
        return values


class NumericValidityColumn(StrictModel):
    column: str
    valid_range_source: str
    min_value: Optional[float] = None
    max_value: Optional[float] = None

    @validator("column", "valid_range_source")
    def _validate_required_text(cls, value: str, field: Any) -> str:
        return _ensure_non_empty_string(field.name, value)

    @root_validator
    def _validate_range_bounds(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        min_value = values.get("min_value")
        max_value = values.get("max_value")
        if min_value is None and max_value is None:
            raise ValueError("numeric validity columns must declare at least one bound")
        if min_value is not None and max_value is not None and min_value > max_value:
            raise ValueError("numeric validity min_value cannot exceed max_value")
        return values


class DuplicatePolicy(StrictModel):
    definition: Optional[str] = None
    key_columns: List[str] = Field(default_factory=list)

    @validator("definition")
    def _validate_definition(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        return _ensure_non_empty_string("definition", value)

    @validator("key_columns", each_item=True)
    def _validate_key_columns(cls, value: str) -> str:
        return _ensure_non_empty_string("key_columns", value)

    @root_validator
    def _validate_duplicate_policy(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if not values.get("definition") and not values.get("key_columns"):
            raise ValueError("duplicate_policy must provide a definition or at least one key column")
        return values


class ForeignKeyColumn(StrictModel):
    column: str
    support_table: str
    reference_column: str

    @validator("column", "support_table", "reference_column")
    def _validate_required_text(cls, value: str, field: Any) -> str:
        return _ensure_non_empty_string(field.name, value)


class SupportTableReference(StrictModel):
    table_id: str
    join_key: str

    @validator("table_id", "join_key")
    def _validate_required_text(cls, value: str, field: Any) -> str:
        return _ensure_non_empty_string(field.name, value)


class FaultSamplingFrame(StrictModel):
    fault_family: str
    enabled: bool
    scope_level: str
    candidate_scope_refs: List[str] = Field(default_factory=list)
    selection_policy: str

    @validator("fault_family")
    def _validate_fault_family(cls, value: str) -> str:
        value = _ensure_non_empty_string("fault_family", value)
        if value not in VALID_FAULT_FAMILIES:
            raise ValueError(f"fault_family must be one of {VALID_FAULT_FAMILIES}")
        return value

    @validator("scope_level")
    def _validate_scope_level(cls, value: str) -> str:
        value = _ensure_non_empty_string("scope_level", value)
        if value not in {"table", "column"}:
            raise ValueError("scope_level must be 'table' or 'column'")
        return value

    @validator("candidate_scope_refs", each_item=True)
    def _validate_candidate_scope_refs(cls, value: str) -> str:
        return _ensure_non_empty_string("candidate_scope_refs", value)

    @validator("selection_policy")
    def _validate_selection_policy(cls, value: str) -> str:
        return _ensure_non_empty_string("selection_policy", value)

    @root_validator
    def _validate_enabled_frames(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        enabled = values.get("enabled")
        candidates = values.get("candidate_scope_refs") or []
        if enabled and not candidates:
            raise ValueError("enabled fault sampling frames must include at least one candidate scope reference")
        return values


class MonitoredScopeCatalog(StrictModel):
    domain_id: str
    monitored_completeness_columns: List[str] = Field(..., min_items=1)
    monitored_numeric_validity_columns: List[NumericValidityColumn] = Field(default_factory=list)
    duplicate_policy: DuplicatePolicy
    monitored_foreign_key_columns: List[ForeignKeyColumn] = Field(default_factory=list)
    declared_public_support_tables: List[SupportTableReference] = Field(default_factory=list)
    batch_schedule_policy: str
    calendar_construction_policy: str
    admissible_target_scope_sampling_frames: List[FaultSamplingFrame] = Field(..., min_items=1)

    @validator("domain_id")
    def _validate_domain_id(cls, value: str) -> str:
        value = _ensure_non_empty_string("domain_id", value)
        if value not in VALID_DOMAINS:
            raise ValueError(f"domain_id must be one of {VALID_DOMAINS}")
        return value

    @validator("monitored_completeness_columns", each_item=True)
    def _validate_monitored_columns(cls, value: str) -> str:
        return _ensure_non_empty_string("monitored_completeness_columns", value)

    @validator("batch_schedule_policy", "calendar_construction_policy")
    def _validate_policy_text(cls, value: str, field: Any) -> str:
        return _ensure_non_empty_string(field.name, value)

    @root_validator
    def _validate_sampling_frame_coverage(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        frames = values.get("admissible_target_scope_sampling_frames") or []
        fault_families = [frame.fault_family for frame in frames]
        if len(set(fault_families)) != len(fault_families):
            raise ValueError("fault sampling frames must not repeat the same fault_family")
        if set(fault_families) != set(VALID_FAULT_FAMILIES):
            raise ValueError("fault sampling frames must declare coverage for every locked fault family")
        return values


class CalibrationFailureRecord(StrictModel):
    batch_id: str
    failure_type: str
    description: str

    @validator("batch_id", "failure_type", "description")
    def _validate_required_text(cls, value: str, field: Any) -> str:
        return _ensure_non_empty_string(field.name, value)


class BatchRange(StrictModel):
    start_batch: str
    end_batch: str
    batch_count: int = Field(..., ge=1)

    @validator("start_batch", "end_batch")
    def _validate_batch_bounds(cls, value: str, field: Any) -> str:
        return _ensure_non_empty_string(field.name, value)

    @root_validator
    def _validate_batch_order(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        start_batch = values.get("start_batch")
        end_batch = values.get("end_batch")
        if start_batch and end_batch and start_batch > end_batch:
            raise ValueError("start_batch must not sort after end_batch")
        return values


class CalibrationCleanlinessReport(StrictModel):
    domain_id: str
    snapshot_id: str
    candidate_calibration_range: BatchRange
    removed_failures: List[CalibrationFailureRecord] = Field(default_factory=list)
    excluded_batches: List[str] = Field(default_factory=list)
    deterministic_exclusion_rule: str
    final_screened_clean_calibration_batches: int = Field(..., ge=0)

    @validator("domain_id")
    def _validate_domain_id(cls, value: str) -> str:
        value = _ensure_non_empty_string("domain_id", value)
        if value not in VALID_DOMAINS:
            raise ValueError(f"domain_id must be one of {VALID_DOMAINS}")
        return value

    @validator("snapshot_id", "deterministic_exclusion_rule")
    def _validate_required_text(cls, value: str, field: Any) -> str:
        return _ensure_non_empty_string(field.name, value)

    @validator("excluded_batches", each_item=True)
    def _validate_excluded_batches(cls, value: str) -> str:
        return _ensure_non_empty_string("excluded_batches", value)

    @root_validator
    def _validate_cleanliness_counts(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        candidate_range = values.get("candidate_calibration_range")
        final_count = values.get("final_screened_clean_calibration_batches")
        excluded_batches = values.get("excluded_batches") or []
        if len(set(excluded_batches)) != len(excluded_batches):
            raise ValueError("excluded_batches must not contain duplicates")
        if candidate_range is not None and final_count is not None and final_count > candidate_range.batch_count:
            raise ValueError("final_screened_clean_calibration_batches cannot exceed candidate batch_count")
        return values


class InjectionManifest(StrictModel):
    domain_id: str
    fault_family: str
    injection_operator_family: str
    parameter_ranges: Dict[str, Any]
    seed_semantics: str
    edit_budget_or_batch_manipulation_policy: str
    plausibility_guards_on_non_target_features: List[str] = Field(..., min_items=1)
    target_scope_selection_policy: str
    lag_implementation: Optional[str] = None

    @validator("domain_id")
    def _validate_injection_domain_id(cls, value: str) -> str:
        value = _ensure_non_empty_string("domain_id", value)
        if value not in VALID_DOMAINS:
            raise ValueError(f"domain_id must be one of {VALID_DOMAINS}")
        return value

    @validator("fault_family")
    def _validate_injection_fault_family(cls, value: str) -> str:
        value = _ensure_non_empty_string("fault_family", value)
        if value not in VALID_FAULT_FAMILIES:
            raise ValueError(f"fault_family must be one of {VALID_FAULT_FAMILIES}")
        return value

    @validator("injection_operator_family", "seed_semantics", "edit_budget_or_batch_manipulation_policy", "target_scope_selection_policy")
    def _validate_injection_text_fields(cls, value: str, field: Any) -> str:
        return _ensure_non_empty_string(field.name, value)

    @validator("parameter_ranges")
    def _validate_parameter_ranges(cls, value: Dict[str, Any]) -> Dict[str, Any]:
        if not value:
            raise ValueError("parameter_ranges must not be empty")
        _validate_json_like(value, "parameter_ranges")
        return value

    @validator("plausibility_guards_on_non_target_features", each_item=True)
    def _validate_plausibility_guards(cls, value: str) -> str:
        return _ensure_non_empty_string("plausibility_guards_on_non_target_features", value)

    @validator("lag_implementation")
    def _validate_lag_implementation(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        normalized = _ensure_non_empty_string("lag_implementation", value).lower().replace(" ", "_")
        if normalized not in {"delayed_arrival", "omitted_batch_materialization", "both"}:
            raise ValueError(
                "lag_implementation must be one of 'delayed_arrival', 'omitted_batch_materialization', or 'both'"
            )
        return normalized

    @root_validator
    def _validate_freshness_specific_fields(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        fault_family = values.get("fault_family")
        lag_implementation = values.get("lag_implementation")
        if fault_family == "freshness_lag" and lag_implementation is None:
            raise ValueError("freshness_lag injection manifests must declare lag_implementation")
        if fault_family != "freshness_lag" and lag_implementation is not None:
            raise ValueError("lag_implementation is only valid for freshness_lag injection manifests")
        return values


class DetectorConfigurationManifest(StrictModel):
    detector_id: str
    detector_family: str
    parameters: Dict[str, Any]
    calibration_policies: List[str] = Field(..., min_items=1)

    @validator("detector_id", "detector_family")
    def _validate_required_text(cls, value: str, field: Any) -> str:
        return _ensure_non_empty_string(field.name, value)

    @validator("parameters")
    def _validate_parameters(cls, value: Dict[str, Any]) -> Dict[str, Any]:
        if not value:
            raise ValueError("parameters must not be empty")
        _validate_json_like(value, "parameters")
        return value

    @validator("calibration_policies", each_item=True)
    def _validate_calibration_policies(cls, value: str) -> str:
        return _ensure_non_empty_string("calibration_policies", value)


class SoftwareVersionManifest(StrictModel):
    detector_id: str
    python_version: str
    package_versions: Dict[str, str]

    @validator("detector_id", "python_version")
    def _validate_required_text(cls, value: str, field: Any) -> str:
        return _ensure_non_empty_string(field.name, value)

    @validator("package_versions")
    def _validate_package_versions(cls, value: Dict[str, str]) -> Dict[str, str]:
        if not value:
            raise ValueError("package_versions must not be empty")
        for key, item in value.items():
            _ensure_non_empty_string("package_versions key", key)
            _ensure_non_empty_string(f"package_versions.{key}", item)
        return value


class RuntimeManifest(StrictModel):
    runtime_boundary: str
    hardware_specification: Dict[str, Any]
    thread_count_policy: str
    cache_policy: str
    environment: Dict[str, Any]

    @validator("runtime_boundary", "thread_count_policy", "cache_policy")
    def _validate_required_text(cls, value: str, field: Any) -> str:
        return _ensure_non_empty_string(field.name, value)

    @validator("hardware_specification", "environment")
    def _validate_runtime_mappings(cls, value: Dict[str, Any], field: Any) -> Dict[str, Any]:
        if not value:
            raise ValueError(f"{field.name} must not be empty")
        _validate_json_like(value, field.name)
        return value


class SchemaValidationIssue(StrictModel):
    location: str
    message: str
    severity: str

    @validator("location", "message")
    def _validate_required_text(cls, value: str, field: Any) -> str:
        return _ensure_non_empty_string(field.name, value)

    @validator("severity")
    def _validate_severity(cls, value: str) -> str:
        value = _ensure_non_empty_string("severity", value)
        if value not in {"error", "warning"}:
            raise ValueError("severity must be 'error' or 'warning'")
        return value


class SchemaValidationReport(StrictModel):
    artifact_type: str
    artifact_path: str
    validator_name: str
    passed: bool
    issues: List[SchemaValidationIssue] = Field(default_factory=list)

    @validator("artifact_type", "artifact_path", "validator_name")
    def _validate_required_text(cls, value: str, field: Any) -> str:
        return _ensure_non_empty_string(field.name, value)

    @root_validator
    def _validate_issue_consistency(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        passed = values.get("passed")
        issues = values.get("issues") or []
        has_error = any(issue.severity == "error" for issue in issues)
        if not passed and not issues:
            raise ValueError("failed schema validation reports must include at least one issue")
        if passed and has_error:
            raise ValueError("passed schema validation reports cannot include error issues")
        return values
