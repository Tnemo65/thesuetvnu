import pandas as pd

from dqbench.data.profiling import build_batch_profiles
from dqbench.data.samples import generate_tlc_sample
from dqbench.data.tlc import TLCDatasetAdapter
from dqbench.injection.registry import build_injector


def _prepared_tlc():
    raw_df, support_tables = generate_tlc_sample(days=10, rows_per_day=30, seed=42)
    return TLCDatasetAdapter().prepare(raw_df, support_tables=support_tables)


def test_null_spike_increases_null_ratio():
    prepared = _prepared_tlc()
    injector = build_injector("null_spike")
    result = injector.inject(
        clean_df=prepared.canonical_df,
        batch_index=prepared.batch_index,
        run_id="run",
        domain="tlc",
        config={
            "severity": "high",
            "duration": "one_window",
            "target_column": "fare_amount",
            "table_ref": "tlc_trips",
            "severity_map": {"low": 0.1, "medium": 0.25, "high": 0.5},
        },
        seed=1,
    )
    profile_df = build_batch_profiles(
        result.dirty_df,
        {
            "batch_col": "batch_id",
            "null_columns": ["fare_amount"],
            "duplicate_key": [],
            "range_columns": {},
            "fk_columns": {},
        },
    )
    assert profile_df["null_ratio__fare_amount"].max() > 0.3


def test_duplicate_burst_and_freshness_change_row_counts():
    prepared = _prepared_tlc()
    duplicate_result = build_injector("duplicate_burst").inject(
        clean_df=prepared.canonical_df,
        batch_index=prepared.batch_index,
        run_id="run",
        domain="tlc",
        config={"severity": "medium", "duration": "one_window", "table_ref": "tlc_trips", "severity_map": {"low": 0.1, "medium": 0.25, "high": 0.5}},
        seed=2,
    )
    freshness_result = build_injector("freshness_lag").inject(
        clean_df=prepared.canonical_df,
        batch_index=prepared.batch_index,
        run_id="run",
        domain="tlc",
        config={"severity": "medium", "duration": "one_window", "table_ref": "tlc_trips", "mode": "missing", "delay_days_map": {"low": 1, "medium": 2, "high": 3}},
        seed=3,
    )
    assert len(duplicate_result.dirty_df) > len(prepared.canonical_df)
    assert len(freshness_result.dirty_df) < len(prepared.canonical_df)


def test_range_and_fk_break_create_invalid_values():
    prepared = _prepared_tlc()
    range_result = build_injector("range_violation").inject(
        clean_df=prepared.canonical_df,
        batch_index=prepared.batch_index,
        run_id="run",
        domain="tlc",
        config={
            "severity": "high",
            "duration": "one_window",
            "target_column": "trip_distance",
            "table_ref": "tlc_trips",
            "min": 0.0,
            "max": 100.0,
            "severity_map": {"low": 0.1, "medium": 0.25, "high": 0.5},
            "delta_map": {"low": 20.0, "medium": 50.0, "high": 100.0},
        },
        seed=4,
    )
    fk_result = build_injector("fk_break").inject(
        clean_df=prepared.canonical_df,
        batch_index=prepared.batch_index,
        run_id="run",
        domain="tlc",
        config={
            "severity": "high",
            "duration": "one_window",
            "target_column": "PULocationID",
            "table_ref": "tlc_trips",
            "relation_ref": "tlc_trips:taxi_zone_lookup",
            "invalid_value": 9999,
            "severity_map": {"low": 0.05, "medium": 0.15, "high": 0.30},
        },
        seed=5,
    )
    assert range_result.dirty_df["trip_distance"].max() > 100.0
    assert (fk_result.dirty_df["PULocationID"] == 9999).any()
