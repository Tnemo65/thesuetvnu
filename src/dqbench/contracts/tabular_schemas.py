"""Pandera schemas for canonical tabular artifacts."""

from __future__ import annotations

from typing import Iterable

import pandas as pd
import pandera.pandas as pa
from pandera import Check

from dqbench.contracts.benchmark import (
    PRIMARY_METRICS,
    SUPPLEMENTARY_METRICS,
    VALID_CALIBRATIONS,
    VALID_DOMAINS,
    VALID_DURATIONS,
    VALID_FAULT_FAMILIES,
    VALID_SCOPE_LEVELS,
    VALID_SEVERITIES,
)


def _is_mapping(value: object) -> bool:
    return isinstance(value, dict)


def _non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _nullable_non_empty_string(value: object) -> bool:
    return value is None or _non_empty_string(value)


def _required_columns(columns: Iterable[str]) -> dict[str, pa.Column]:
    return {
        column: pa.Column(None, nullable=False, required=True)
        for column in columns
    }


def canonical_dataframe_schema(required_columns: Iterable[str] | None = None) -> pa.DataFrameSchema:
    columns = {
        "event_ts": pa.Column(pa.DateTime, nullable=False),
        "event_date": pa.Column(pa.DateTime, nullable=False),
        "batch_id": pa.Column(pa.String, nullable=False, checks=Check.str_length(min_value=1)),
    }
    if required_columns:
        columns.update(_required_columns(required_columns))
    return pa.DataFrameSchema(columns=columns, strict=False, coerce=False)


def support_table_schema(required_columns: Iterable[str]) -> pa.DataFrameSchema:
    columns = {
        column: pa.Column(None, nullable=False, required=True)
        for column in required_columns
    }
    return pa.DataFrameSchema(
        columns=columns,
        strict=False,
        coerce=False,
        checks=Check(lambda df: len(df) > 0, error="support tables must not be empty"),
    )


def canonical_batch_index_schema() -> pa.DataFrameSchema:
    return pa.DataFrameSchema(
        columns={
            "batch_id": pa.Column(pa.String, nullable=False, checks=Check.str_length(min_value=1)),
            "start_time": pa.Column(pa.DateTime, nullable=False),
            "end_time": pa.Column(pa.DateTime, nullable=False),
            "row_count": pa.Column(pa.Int, nullable=False, checks=Check.ge(0)),
            "batch_order": pa.Column(pa.Int, nullable=False, checks=Check.ge(0)),
            "is_missing": pa.Column(pa.Bool, nullable=False),
            "is_delayed": pa.Column(pa.Bool, nullable=False),
        },
        unique=["batch_id", "batch_order"],
        strict=True,
        coerce=True,
        checks=Check(lambda df: (df["start_time"] <= df["end_time"]).all(), error="start_time must be <= end_time"),
    )


def _ratio_column(nullable: bool = True, required: bool = True, regex: bool = False) -> pa.Column:
    return pa.Column(pa.Float, nullable=nullable, required=required, regex=regex, checks=Check.in_range(0.0, 1.0))


def _non_negative_float(nullable: bool = True, required: bool = True) -> pa.Column:
    return pa.Column(pa.Float, nullable=nullable, required=required, checks=Check.ge(0.0))


def batch_profile_schema() -> pa.DataFrameSchema:
    return pa.DataFrameSchema(
        columns={
            "batch_id": pa.Column(pa.String, nullable=False, checks=Check.str_length(min_value=1)),
            "row_count": pa.Column(pa.Int, nullable=False, checks=Check.ge(0)),
            "duplicate_ratio": _ratio_column(nullable=False),
            r"^null_ratio__.+$": _ratio_column(regex=True),
            r"^range_violation_ratio__.+$": _ratio_column(regex=True),
            r"^invalid_fk_ratio__.+$": _ratio_column(regex=True),
            r"^min__.+$": pa.Column(pa.Float, nullable=True, regex=True),
            r"^max__.+$": pa.Column(pa.Float, nullable=True, regex=True),
        },
        unique=["batch_id"],
        strict=False,
        coerce=True,
    )


def calibration_profile_schema() -> pa.DataFrameSchema:
    return batch_profile_schema()


def evaluation_profile_schema() -> pa.DataFrameSchema:
    return batch_profile_schema()


def alerts_schema() -> pa.DataFrameSchema:
    return pa.DataFrameSchema(
        columns={
            "alert_id": pa.Column(pa.String, nullable=False, checks=Check.str_length(min_value=1)),
            "run_id": pa.Column(pa.String, nullable=False, checks=Check.str_length(min_value=1)),
            "detector": pa.Column(pa.String, nullable=False, checks=Check.str_length(min_value=1)),
            "domain": pa.Column(pa.String, nullable=False, checks=Check.isin(list(VALID_DOMAINS))),
            "batch_id": pa.Column(pa.String, nullable=False, checks=Check.str_length(min_value=1)),
            "scope_level": pa.Column(pa.String, nullable=False, checks=Check.isin(list(VALID_SCOPE_LEVELS))),
            "scope_ref": pa.Column(pa.String, nullable=False, checks=Check.str_length(min_value=1)),
            "score": _non_negative_float(nullable=False),
            "calibration_policy": pa.Column(pa.String, nullable=False, checks=Check.isin(list(VALID_CALIBRATIONS))),
            "payload": pa.Column(
                object,
                nullable=False,
                checks=Check(lambda series: series.map(_is_mapping).all(), error="payload must be a mapping"),
            ),
        },
        unique=["alert_id"],
        strict=True,
        coerce=True,
    )


def incidents_schema() -> pa.DataFrameSchema:
    return pa.DataFrameSchema(
        columns={
            "incident_id": pa.Column(pa.String, nullable=False, checks=Check.str_length(min_value=1)),
            "run_id": pa.Column(pa.String, nullable=False, checks=Check.str_length(min_value=1)),
            "domain": pa.Column(pa.String, nullable=False, checks=Check.isin(list(VALID_DOMAINS))),
            "family": pa.Column(pa.String, nullable=False, checks=Check.isin(list(VALID_FAULT_FAMILIES))),
            "severity": pa.Column(pa.String, nullable=False, checks=Check.isin(list(VALID_SEVERITIES))),
            "duration": pa.Column(pa.String, nullable=False, checks=Check.isin(list(VALID_DURATIONS))),
            "target_scope": pa.Column(
                object,
                nullable=False,
                checks=Check(lambda series: series.map(_is_mapping).all(), error="target_scope must be a mapping"),
            ),
            "start_batch": pa.Column(pa.String, nullable=False, checks=Check.str_length(min_value=1)),
            "end_batch": pa.Column(pa.String, nullable=False, checks=Check.str_length(min_value=1)),
            "window_start": pa.Column(pa.String, nullable=False, checks=Check.str_length(min_value=1)),
            "window_end": pa.Column(pa.String, nullable=False, checks=Check.str_length(min_value=1)),
            "metadata": pa.Column(
                object,
                nullable=False,
                checks=Check(lambda series: series.map(_is_mapping).all(), error="metadata must be a mapping"),
            ),
        },
        unique=["incident_id"],
        strict=True,
        coerce=True,
        checks=[
            Check(lambda df: (df["start_batch"] <= df["end_batch"]).all(), error="start_batch must be <= end_batch"),
            Check(lambda df: (df["window_start"] <= df["window_end"]).all(), error="window_start must be <= window_end"),
            Check(
                lambda df: ((df["window_start"] <= df["start_batch"]) & (df["end_batch"] <= df["window_end"])).all(),
                error="incident interval must lie inside the detection window",
            ),
        ],
    )


def matches_schema() -> pa.DataFrameSchema:
    return pa.DataFrameSchema(
        columns={
            "record_type": pa.Column(
                pa.String,
                nullable=False,
                checks=Check.isin(["matched_pair", "duplicate_alert", "unmatched_alert", "missed_incident"]),
            ),
            "alert_id": pa.Column(
                object,
                nullable=True,
                checks=Check(lambda series: series.map(_nullable_non_empty_string).all(), error="alert_id must be null or non-empty"),
            ),
            "incident_id": pa.Column(
                object,
                nullable=True,
                checks=Check(
                    lambda series: series.map(_nullable_non_empty_string).all(),
                    error="incident_id must be null or non-empty",
                ),
            ),
        },
        strict=True,
        coerce=True,
        checks=[
            Check(
                lambda df: (
                    (df["record_type"].isin(["matched_pair", "duplicate_alert", "unmatched_alert"]) == df["alert_id"].notna())
                ).all(),
                error="alert-bearing match rows must carry alert_id and only those rows may do so",
            ),
            Check(
                lambda df: (
                    (df["record_type"].isin(["matched_pair", "duplicate_alert", "missed_incident"]) == df["incident_id"].notna())
                ).all(),
                error="incident-bearing match rows must carry incident_id and only those rows may do so",
            ),
        ],
    )


def metrics_schema() -> pa.DataFrameSchema:
    return pa.DataFrameSchema(
        columns={
            "incident_recall": _ratio_column(required=True),
            "incident_precision": _ratio_column(required=True),
            "incident_f1": _ratio_column(required=True),
            "detection_delay_raw_mean": _non_negative_float(required=True),
            "detection_delay_norm_mean": _ratio_column(required=True),
            "localization_accuracy_strict": _ratio_column(required=True),
            "localization_accuracy_hierarchical": _ratio_column(required=True),
            "duplicate_burden": _non_negative_float(required=True),
            "clean_run_fp_batch": _ratio_column(required=True),
            "clean_run_fp_alert": _non_negative_float(required=True),
            "runtime_overhead_seconds": _non_negative_float(nullable=False, required=True),
            "runtime_per_1m_rows": _non_negative_float(required=True),
            "weak_label_hit_rate": _ratio_column(required=False),
            "weak_label_lead_lag_median": pa.Column(pa.Float, nullable=True, required=False),
        },
        strict=True,
        coerce=True,
        checks=Check(lambda df: len(df) == 1, error="metrics artifact must contain exactly one row"),
    )


TABULAR_SCHEMA_REGISTRY = {
    "canonical_dataframe": canonical_dataframe_schema,
    "support_tables": support_table_schema,
    "canonical_batch_index": canonical_batch_index_schema,
    "calibration_profiles": calibration_profile_schema,
    "evaluation_profiles": evaluation_profile_schema,
    "alerts": alerts_schema,
    "incidents": incidents_schema,
    "matches": matches_schema,
    "metrics": metrics_schema,
}


PRIMARY_METRIC_COLUMNS = tuple(PRIMARY_METRICS)
SUPPLEMENTARY_METRIC_COLUMNS = tuple(SUPPLEMENTARY_METRICS)


def validate_dataframe(schema: pa.DataFrameSchema, df: pd.DataFrame) -> pd.DataFrame:
    return schema.validate(df, lazy=True)
