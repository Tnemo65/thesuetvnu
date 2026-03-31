"""Helpers to validate benchmark artifacts and emit schema-validation reports."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any, Callable, Dict, Iterable, List, Mapping

import pandas as pd
import pandera.errors as pa_errors
import pandera.pandas as pa
from pydantic import ValidationError as PydanticValidationError

from dqbench.contracts.manifests import SchemaValidationIssue, SchemaValidationReport
from dqbench.contracts.output_artifacts import (
    SchemaValidationArtifact,
    validate_alert_artifact,
    validate_incident_artifact,
    validate_match_artifact,
    validate_metrics_artifact,
    validate_schema_validation_artifact,
)
from dqbench.contracts.tabular_schemas import alerts_schema, incidents_schema, matches_schema, metrics_schema
from dqbench.evaluation.matching import MatchResult


def _normalize_record(record: Any) -> Dict[str, Any]:
    if is_dataclass(record):
        return asdict(record)
    if isinstance(record, Mapping):
        return dict(record)
    raise TypeError(f"Expected dataclass or mapping record, got {type(record)!r}")


def normalize_alert_records(alerts: Iterable[Any]) -> List[Dict[str, Any]]:
    return [_normalize_record(alert) for alert in alerts]


def normalize_incident_records(incidents: Iterable[Any]) -> List[Dict[str, Any]]:
    return [_normalize_record(incident) for incident in incidents]


def normalize_match_artifact(match_result: MatchResult) -> Dict[str, Any]:
    return {
        "matched_pairs": [
            {"alert_id": alert.alert_id, "incident_id": incident.incident_id}
            for alert, incident in match_result.matched_pairs
        ],
        "duplicate_alert_ids": [alert.alert_id for alert in match_result.duplicate_alerts],
        "unmatched_alert_ids": [alert.alert_id for alert in match_result.unmatched_alerts],
        "missed_incident_ids": [incident.incident_id for incident in match_result.missed_incidents],
    }


def normalize_match_records(match_result: MatchResult) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    rows.extend(
        {"record_type": "matched_pair", "alert_id": alert.alert_id, "incident_id": incident.incident_id}
        for alert, incident in match_result.matched_pairs
    )
    rows.extend(
        {"record_type": "duplicate_alert", "alert_id": alert.alert_id, "incident_id": incident_id}
        for incident_id, alerts in match_result.duplicates_by_incident.items()
        for alert in alerts
    )
    rows.extend(
        {"record_type": "unmatched_alert", "alert_id": alert.alert_id, "incident_id": None}
        for alert in match_result.unmatched_alerts
    )
    rows.extend(
        {"record_type": "missed_incident", "alert_id": None, "incident_id": incident.incident_id}
        for incident in match_result.missed_incidents
    )
    return rows


def _frame_from_records(records: List[Dict[str, Any]], columns: List[str]) -> pd.DataFrame:
    if not records:
        return pd.DataFrame(columns=columns)
    return pd.DataFrame(records)


def _pandera_issues(exc: Exception) -> List[SchemaValidationIssue]:
    if isinstance(exc, pa_errors.SchemaErrors):
        failure_cases = exc.failure_cases.fillna("")
        issues: List[SchemaValidationIssue] = []
        for _, row in failure_cases.iterrows():
            column = str(row.get("column") or row.get("schema_context") or "dataframe")
            failure_case = str(row.get("failure_case") or row.get("check") or row.get("message") or "schema failure")
            issues.append(
                SchemaValidationIssue(location=column, message=failure_case, severity="error")
            )
        return issues or [SchemaValidationIssue(location="dataframe", message=str(exc), severity="error")]
    if isinstance(exc, pa_errors.SchemaError):
        return [SchemaValidationIssue(location="dataframe", message=str(exc), severity="error")]
    return [SchemaValidationIssue(location="dataframe", message=str(exc), severity="error")]


def _pydantic_issues(exc: Exception) -> List[SchemaValidationIssue]:
    if isinstance(exc, PydanticValidationError):
        return [
            SchemaValidationIssue(
                location=".".join(str(part) for part in err["loc"]),
                message=err["msg"],
                severity="error",
            )
            for err in exc.errors()
        ]
    return [SchemaValidationIssue(location="artifact", message=str(exc), severity="error")]


def validate_with_pandera(
    *,
    artifact_type: str,
    artifact_path: str,
    schema: pa.DataFrameSchema,
    dataframe: pd.DataFrame,
) -> SchemaValidationReport:
    try:
        schema.validate(dataframe, lazy=True)
        return SchemaValidationReport(
            artifact_type=artifact_type,
            artifact_path=artifact_path,
            validator_name="pandera",
            passed=True,
            issues=[],
        )
    except Exception as exc:
        return SchemaValidationReport(
            artifact_type=artifact_type,
            artifact_path=artifact_path,
            validator_name="pandera",
            passed=False,
            issues=_pandera_issues(exc),
        )


def validate_with_pydantic(
    *,
    artifact_type: str,
    artifact_path: str,
    validator: Callable[[Any], Any],
    payload: Any,
) -> SchemaValidationReport:
    try:
        validator(payload)
        return SchemaValidationReport(
            artifact_type=artifact_type,
            artifact_path=artifact_path,
            validator_name="pydantic",
            passed=True,
            issues=[],
        )
    except Exception as exc:
        return SchemaValidationReport(
            artifact_type=artifact_type,
            artifact_path=artifact_path,
            validator_name="pydantic",
            passed=False,
            issues=_pydantic_issues(exc),
        )


def build_run_schema_validation_artifact(
    *,
    output_dir: str,
    alerts: Iterable[Any],
    incidents: Iterable[Any],
    match_result: MatchResult,
    metrics: Dict[str, Any],
) -> Dict[str, Any]:
    alert_records = normalize_alert_records(alerts)
    incident_records = normalize_incident_records(incidents)
    match_artifact = normalize_match_artifact(match_result)
    match_records = normalize_match_records(match_result)

    reports = [
        validate_with_pandera(
            artifact_type="alerts",
            artifact_path=f"{output_dir}/alerts.json",
            schema=alerts_schema(),
            dataframe=_frame_from_records(
                alert_records,
                [
                    "alert_id",
                    "run_id",
                    "detector",
                    "domain",
                    "batch_id",
                    "scope_level",
                    "scope_ref",
                    "score",
                    "calibration_policy",
                    "payload",
                ],
            ),
        ),
        validate_with_pydantic(
            artifact_type="alerts",
            artifact_path=f"{output_dir}/alerts.json",
            validator=validate_alert_artifact,
            payload=alert_records,
        ),
        validate_with_pandera(
            artifact_type="incidents",
            artifact_path=f"{output_dir}/incidents.json",
            schema=incidents_schema(),
            dataframe=_frame_from_records(
                incident_records,
                [
                    "incident_id",
                    "run_id",
                    "domain",
                    "family",
                    "severity",
                    "duration",
                    "target_scope",
                    "start_batch",
                    "end_batch",
                    "window_start",
                    "window_end",
                    "metadata",
                ],
            ),
        ),
        validate_with_pydantic(
            artifact_type="incidents",
            artifact_path=f"{output_dir}/incidents.json",
            validator=validate_incident_artifact,
            payload=incident_records,
        ),
        validate_with_pandera(
            artifact_type="matches",
            artifact_path=f"{output_dir}/matches.json",
            schema=matches_schema(),
            dataframe=_frame_from_records(match_records, ["record_type", "alert_id", "incident_id"]),
        ),
        validate_with_pydantic(
            artifact_type="matches",
            artifact_path=f"{output_dir}/matches.json",
            validator=validate_match_artifact,
            payload=match_artifact,
        ),
        validate_with_pandera(
            artifact_type="metrics",
            artifact_path=f"{output_dir}/metrics.json",
            schema=metrics_schema(),
            dataframe=pd.DataFrame([metrics]),
        ),
        validate_with_pydantic(
            artifact_type="metrics",
            artifact_path=f"{output_dir}/metrics.json",
            validator=validate_metrics_artifact,
            payload=metrics,
        ),
    ]

    artifact = SchemaValidationArtifact(reports=reports)
    payload = artifact.dict()
    validate_schema_validation_artifact(payload)
    return payload
