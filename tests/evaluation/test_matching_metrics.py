from dqbench.contracts.alerts import AlertRecord
from dqbench.contracts.incidents import IncidentRecord
from dqbench.evaluation.matching import match_alerts
from dqbench.evaluation.metrics import compute_metrics


def test_matching_and_metrics_capture_duplicates_and_delay():
    incident = IncidentRecord.from_dict(
        {
            "incident_id": "i1",
            "run_id": "r1",
            "domain": "tlc",
            "family": "null_spike",
            "severity": "medium",
            "duration": "one_window",
            "target_scope": {"level": "column", "ref": "tlc_trips.fare_amount", "table_ref": "tlc_trips"},
            "start_batch": "2025-01-02",
            "end_batch": "2025-01-02",
            "window_start": "2025-01-02",
            "window_end": "2025-01-02",
            "metadata": {},
        }
    )
    alerts = [
        AlertRecord.from_dict(
            {
                "alert_id": "a1",
                "run_id": "r1",
                "detector": "naive_threshold",
                "domain": "tlc",
                "batch_id": "2025-01-02",
                "scope_level": "column",
                "scope_ref": "tlc_trips.fare_amount",
                "score": 5.0,
                "calibration_policy": "percentile_95",
                "payload": {},
            }
        ),
        AlertRecord.from_dict(
            {
                "alert_id": "a2",
                "run_id": "r1",
                "detector": "naive_threshold",
                "domain": "tlc",
                "batch_id": "2025-01-02",
                "scope_level": "column",
                "scope_ref": "tlc_trips.fare_amount",
                "score": 4.2,
                "calibration_policy": "percentile_95",
                "payload": {},
            }
        ),
    ]
    batch_index = __import__("pandas").DataFrame(
        {
            "batch_id": ["2025-01-01", "2025-01-02", "2025-01-03"],
            "batch_order": [0, 1, 2],
        }
    )
    result = match_alerts(alerts, [incident])
    metrics = compute_metrics(result, batch_index=batch_index, runtime_seconds=1.2, row_count=100)
    assert len(result.matched_pairs) == 1
    assert len(result.duplicate_alerts) == 1
    assert metrics["incident_recall"] == 1.0
    assert metrics["duplicate_burden"] == 1.0
    assert metrics["detection_delay_raw_mean"] == 0.0
