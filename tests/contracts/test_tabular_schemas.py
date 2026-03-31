import pandas as pd
import pandera.errors as pa_errors
import pytest

from dqbench.contracts.tabular_schemas import (
    alerts_schema,
    calibration_profile_schema,
    canonical_batch_index_schema,
    canonical_dataframe_schema,
    incidents_schema,
    matches_schema,
    metrics_schema,
    support_table_schema,
)


PANDERA_ERRORS = (pa_errors.SchemaError, pa_errors.SchemaErrors)


def test_canonical_dataframe_support_table_and_batch_index_schemas_accept_valid_frames():
    canonical_df = pd.DataFrame(
        {
            "event_ts": pd.to_datetime(["2025-01-01T08:00:00", "2025-01-01T09:00:00"]),
            "event_date": pd.to_datetime(["2025-01-01", "2025-01-01"]),
            "batch_id": ["2025-01-01", "2025-01-01"],
            "fare_amount": [14.5, 21.0],
        }
    )
    support_df = pd.DataFrame({"LocationID": [1, 2], "Zone": ["A", "B"]})
    batch_index_df = pd.DataFrame(
        {
            "batch_id": ["2025-01-01", "2025-01-02"],
            "start_time": pd.to_datetime(["2025-01-01", "2025-01-02"]),
            "end_time": pd.to_datetime(["2025-01-01", "2025-01-02"]),
            "row_count": [2, 0],
            "batch_order": [0, 1],
            "is_missing": [False, True],
            "is_delayed": [False, False],
        }
    )

    canonical_dataframe_schema(required_columns=["fare_amount"]).validate(canonical_df, lazy=True)
    support_table_schema(["LocationID"]).validate(support_df, lazy=True)
    canonical_batch_index_schema().validate(batch_index_df, lazy=True)


def test_profile_schema_rejects_invalid_ratios():
    valid_profile_df = pd.DataFrame(
        {
            "batch_id": ["2025-01-01"],
            "row_count": [10],
            "duplicate_ratio": [0.2],
            "null_ratio__fare_amount": [0.1],
            "range_violation_ratio__fare_amount": [0.0],
            "invalid_fk_ratio__PULocationID": [0.0],
            "min__fare_amount": [2.5],
            "max__fare_amount": [40.0],
        }
    )
    calibration_profile_schema().validate(valid_profile_df, lazy=True)

    invalid_profile_df = valid_profile_df.assign(duplicate_ratio=1.5)
    with pytest.raises(PANDERA_ERRORS):
        calibration_profile_schema().validate(invalid_profile_df, lazy=True)


def test_alert_incident_match_and_metrics_schemas_validate_and_fail_on_bad_linkage():
    alerts_df = pd.DataFrame(
        [
            {
                "alert_id": "a1",
                "run_id": "r1",
                "detector": "custom_detector",
                "domain": "tlc",
                "batch_id": "2025-01-01",
                "scope_level": "column",
                "scope_ref": "tlc_trips.fare_amount",
                "score": 3.4,
                "calibration_policy": "percentile_95",
                "payload": {"top_feature": "null_ratio__fare_amount"},
            }
        ]
    )
    incidents_df = pd.DataFrame(
        [
            {
                "incident_id": "i1",
                "run_id": "r1",
                "domain": "tlc",
                "family": "null_spike",
                "severity": "medium",
                "duration": "one_window",
                "target_scope": {"level": "column", "ref": "tlc_trips.fare_amount", "table_ref": "tlc_trips"},
                "start_batch": "2025-01-01",
                "end_batch": "2025-01-01",
                "window_start": "2025-01-01",
                "window_end": "2025-01-01",
                "metadata": {},
            }
        ]
    )
    matches_df = pd.DataFrame(
        [
            {"record_type": "matched_pair", "alert_id": "a1", "incident_id": "i1"},
            {"record_type": "duplicate_alert", "alert_id": "a2", "incident_id": "i1"},
            {"record_type": "unmatched_alert", "alert_id": "a3", "incident_id": None},
            {"record_type": "missed_incident", "alert_id": None, "incident_id": "i2"},
        ]
    )
    metrics_df = pd.DataFrame(
        [
            {
                "incident_recall": 1.0,
                "incident_precision": 0.5,
                "incident_f1": 2 / 3,
                "detection_delay_raw_mean": 0.0,
                "detection_delay_norm_mean": 0.0,
                "localization_accuracy_strict": 1.0,
                "localization_accuracy_hierarchical": 1.0,
                "duplicate_burden": 1.0,
                "clean_run_fp_batch": None,
                "clean_run_fp_alert": None,
                "runtime_overhead_seconds": 1.2,
                "runtime_per_1m_rows": 12000.0,
            }
        ]
    )

    alerts_schema().validate(alerts_df, lazy=True)
    incidents_schema().validate(incidents_df, lazy=True)
    matches_schema().validate(matches_df, lazy=True)
    metrics_schema().validate(metrics_df, lazy=True)

    invalid_matches_df = pd.DataFrame(
        [{"record_type": "matched_pair", "alert_id": "a1", "incident_id": None}]
    )
    with pytest.raises(PANDERA_ERRORS):
        matches_schema().validate(invalid_matches_df, lazy=True)
