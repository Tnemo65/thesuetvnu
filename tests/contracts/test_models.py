from dqbench.contracts.alerts import AlertRecord
from dqbench.contracts.incidents import IncidentRecord
from dqbench.contracts.runs import RunSpec


def test_run_spec_validates_dirty_run():
    spec = RunSpec.from_dict(
        {
            "domain": "tlc",
            "snapshot_id": "synthetic",
            "batch_unit": "daily",
            "fault_family": "null_spike",
            "severity": "medium",
            "duration": "one_window",
            "seed": 1,
            "detector": "calibration_threshold_lower_bound",
            "calibration_policy": "percentile_95",
        }
    )
    assert spec.seed == 1


def test_incident_and_alert_validate():
    incident = IncidentRecord.from_dict(
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
    )
    alert = AlertRecord.from_dict(
        {
            "alert_id": "a1",
            "run_id": "r1",
            "detector": "calibration_threshold_lower_bound",
            "domain": "tlc",
            "batch_id": "2025-01-01",
            "scope_level": "column",
            "scope_ref": "tlc_trips.fare_amount",
            "score": 4.2,
            "calibration_policy": "percentile_95",
            "payload": {},
        }
    )
    assert incident.incident_id == "i1"
    assert alert.alert_id == "a1"
