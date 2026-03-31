"""Canonical output models and JSON schemas for run artifacts."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

from pydantic import Field, root_validator, validator

from dqbench.contracts.benchmark import (
    VALID_CALIBRATIONS,
    VALID_DOMAINS,
    VALID_DURATIONS,
    VALID_FAULT_FAMILIES,
    VALID_SCOPE_LEVELS,
    VALID_SEVERITIES,
)
from dqbench.contracts.manifests import SchemaValidationReport, StrictModel, _ensure_non_empty_string


def _schema_for_array(model: type[StrictModel], title: str) -> Dict[str, Any]:
    return {
        "title": title,
        "type": "array",
        "items": model.schema(ref_template="#/definitions/{model}"),
    }


class AlertArtifactRecord(StrictModel):
    alert_id: str
    run_id: str
    detector: str
    domain: str
    batch_id: str
    scope_level: str
    scope_ref: str
    score: float
    calibration_policy: str
    payload: Dict[str, Any] = Field(default_factory=dict)

    @validator("alert_id", "run_id", "batch_id", "scope_ref")
    def _validate_non_empty_text(cls, value: str, field: Any) -> str:
        return _ensure_non_empty_string(field.name, value)

    @validator("detector")
    def _validate_detector(cls, value: str) -> str:
        return _ensure_non_empty_string("detector", value)

    @validator("domain")
    def _validate_domain(cls, value: str) -> str:
        value = _ensure_non_empty_string("domain", value)
        if value not in VALID_DOMAINS:
            raise ValueError(f"domain must be one of {VALID_DOMAINS}")
        return value

    @validator("scope_level")
    def _validate_scope_level(cls, value: str) -> str:
        value = _ensure_non_empty_string("scope_level", value)
        if value not in VALID_SCOPE_LEVELS:
            raise ValueError(f"scope_level must be one of {VALID_SCOPE_LEVELS}")
        return value

    @validator("calibration_policy")
    def _validate_calibration_policy(cls, value: str) -> str:
        value = _ensure_non_empty_string("calibration_policy", value)
        if value not in VALID_CALIBRATIONS:
            raise ValueError(f"calibration_policy must be one of {VALID_CALIBRATIONS}")
        return value

    @validator("score")
    def _validate_score(cls, value: float) -> float:
        if value < 0.0:
            raise ValueError("score must be >= 0")
        return value


class TargetScopeRecord(StrictModel):
    level: str
    ref: str
    table_ref: Optional[str] = None
    relation_ref: Optional[str] = None

    @validator("level")
    def _validate_level(cls, value: str) -> str:
        value = _ensure_non_empty_string("level", value)
        if value not in VALID_SCOPE_LEVELS:
            raise ValueError(f"level must be one of {VALID_SCOPE_LEVELS}")
        return value

    @validator("ref")
    def _validate_ref(cls, value: str) -> str:
        return _ensure_non_empty_string("ref", value)

    @validator("table_ref", "relation_ref")
    def _validate_optional_refs(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        return _ensure_non_empty_string("optional_ref", value)


class IncidentArtifactRecord(StrictModel):
    incident_id: str
    run_id: str
    domain: str
    family: str
    severity: str
    duration: str
    target_scope: TargetScopeRecord
    start_batch: str
    end_batch: str
    window_start: str
    window_end: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @validator("incident_id", "run_id", "start_batch", "end_batch", "window_start", "window_end")
    def _validate_non_empty_text(cls, value: str, field: Any) -> str:
        return _ensure_non_empty_string(field.name, value)

    @validator("domain")
    def _validate_domain(cls, value: str) -> str:
        value = _ensure_non_empty_string("domain", value)
        if value not in VALID_DOMAINS:
            raise ValueError(f"domain must be one of {VALID_DOMAINS}")
        return value

    @validator("family")
    def _validate_family(cls, value: str) -> str:
        value = _ensure_non_empty_string("family", value)
        if value not in VALID_FAULT_FAMILIES:
            raise ValueError(f"family must be one of {VALID_FAULT_FAMILIES}")
        return value

    @validator("severity")
    def _validate_severity(cls, value: str) -> str:
        value = _ensure_non_empty_string("severity", value)
        if value not in VALID_SEVERITIES:
            raise ValueError(f"severity must be one of {VALID_SEVERITIES}")
        return value

    @validator("duration")
    def _validate_duration(cls, value: str) -> str:
        value = _ensure_non_empty_string("duration", value)
        if value not in VALID_DURATIONS:
            raise ValueError(f"duration must be one of {VALID_DURATIONS}")
        return value

    @root_validator
    def _validate_batch_windows(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        start_batch = values.get("start_batch")
        end_batch = values.get("end_batch")
        window_start = values.get("window_start")
        window_end = values.get("window_end")
        if start_batch and end_batch and start_batch > end_batch:
            raise ValueError("start_batch must be <= end_batch")
        if window_start and window_end and window_start > window_end:
            raise ValueError("window_start must be <= window_end")
        if start_batch and window_start and start_batch < window_start:
            raise ValueError("incident interval must lie inside the detection window")
        if end_batch and window_end and end_batch > window_end:
            raise ValueError("incident interval must lie inside the detection window")
        return values


class MatchedPairRecord(StrictModel):
    alert_id: str
    incident_id: str

    @validator("alert_id", "incident_id")
    def _validate_ids(cls, value: str, field: Any) -> str:
        return _ensure_non_empty_string(field.name, value)


class MatchArtifact(StrictModel):
    matched_pairs: List[MatchedPairRecord] = Field(default_factory=list)
    duplicate_alert_ids: List[str] = Field(default_factory=list)
    unmatched_alert_ids: List[str] = Field(default_factory=list)
    missed_incident_ids: List[str] = Field(default_factory=list)

    @validator("duplicate_alert_ids", "unmatched_alert_ids", "missed_incident_ids", each_item=True)
    def _validate_id_list(cls, value: str) -> str:
        return _ensure_non_empty_string("match_id", value)

    @root_validator
    def _validate_match_consistency(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        matched_pairs = values.get("matched_pairs") or []
        duplicate_alert_ids = values.get("duplicate_alert_ids") or []
        unmatched_alert_ids = values.get("unmatched_alert_ids") or []
        missed_incident_ids = values.get("missed_incident_ids") or []

        matched_alert_ids = [pair.alert_id for pair in matched_pairs]
        matched_incident_ids = [pair.incident_id for pair in matched_pairs]
        if len(set(matched_alert_ids)) != len(matched_alert_ids):
            raise ValueError("matched_pairs must not repeat alert_id")
        if len(set(matched_incident_ids)) != len(matched_incident_ids):
            raise ValueError("matched_pairs must not repeat incident_id")
        if set(duplicate_alert_ids) & set(unmatched_alert_ids):
            raise ValueError("duplicate_alert_ids and unmatched_alert_ids must be disjoint")
        if set(duplicate_alert_ids) & set(matched_alert_ids):
            raise ValueError("duplicate_alert_ids must exclude the primary matched alert ids")
        if set(missed_incident_ids) & set(matched_incident_ids):
            raise ValueError("missed_incident_ids must exclude matched incident ids")
        return values


class MetricsArtifact(StrictModel):
    incident_recall: Optional[float] = None
    incident_precision: Optional[float] = None
    incident_f1: Optional[float] = None
    detection_delay_raw_mean: Optional[float] = None
    detection_delay_norm_mean: Optional[float] = None
    localization_accuracy_strict: Optional[float] = None
    localization_accuracy_hierarchical: Optional[float] = None
    duplicate_burden: Optional[float] = None
    clean_run_fp_batch: Optional[float] = None
    clean_run_fp_alert: Optional[float] = None
    runtime_overhead_seconds: float
    runtime_per_1m_rows: Optional[float] = None
    weak_label_hit_rate: Optional[float] = None
    weak_label_lead_lag_median: Optional[float] = None

    @validator(
        "incident_recall",
        "incident_precision",
        "incident_f1",
        "detection_delay_norm_mean",
        "localization_accuracy_strict",
        "localization_accuracy_hierarchical",
        "clean_run_fp_batch",
        "clean_run_fp_alert",
        "weak_label_hit_rate",
    )
    def _validate_probability(cls, value: Optional[float]) -> Optional[float]:
        if value is None:
            return value
        if not 0.0 <= value <= 1.0:
            raise ValueError("probability-like metrics must lie in [0, 1]")
        return value

    @validator("detection_delay_raw_mean", "duplicate_burden", "runtime_overhead_seconds", "runtime_per_1m_rows")
    def _validate_non_negative(cls, value: Optional[float]) -> Optional[float]:
        if value is None:
            return value
        if value < 0.0:
            raise ValueError("non-negative metrics must be >= 0")
        return value


class SchemaValidationArtifact(StrictModel):
    reports: List[SchemaValidationReport] = Field(default_factory=list)


CANONICAL_OUTPUT_SCHEMA_REGISTRY: Dict[str, Dict[str, Any]] = {
    "alerts": _schema_for_array(AlertArtifactRecord, "AlertsArtifact"),
    "incidents": _schema_for_array(IncidentArtifactRecord, "IncidentsArtifact"),
    "matches": MatchArtifact.schema(ref_template="#/definitions/{model}"),
    "metrics": MetricsArtifact.schema(ref_template="#/definitions/{model}"),
    "schema_validation": SchemaValidationArtifact.schema(ref_template="#/definitions/{model}"),
}


def validate_alert_artifact(records: Iterable[Dict[str, Any]]) -> List[AlertArtifactRecord]:
    return [AlertArtifactRecord(**record) for record in records]


def validate_incident_artifact(records: Iterable[Dict[str, Any]]) -> List[IncidentArtifactRecord]:
    return [IncidentArtifactRecord(**record) for record in records]


def validate_match_artifact(record: Dict[str, Any]) -> MatchArtifact:
    return MatchArtifact(**record)


def validate_metrics_artifact(record: Dict[str, Any]) -> MetricsArtifact:
    return MetricsArtifact(**record)


def validate_schema_validation_artifact(record: Dict[str, Any]) -> SchemaValidationArtifact:
    return SchemaValidationArtifact(**record)
