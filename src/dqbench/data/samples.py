"""Synthetic sample data for smoke tests and the TLC pilot."""

from __future__ import annotations

from typing import Dict, Tuple

import numpy as np
import pandas as pd


def generate_tlc_sample(days: int = 14, rows_per_day: int = 50, seed: int = 42) -> Tuple[pd.DataFrame, Dict[str, pd.DataFrame]]:
    rng = np.random.default_rng(seed)
    start = pd.Timestamp("2025-01-01")
    total_rows = days * rows_per_day

    pickup_dates = np.repeat(pd.date_range(start, periods=days, freq="D"), rows_per_day)
    pickup_minutes = rng.integers(0, 24 * 60, size=total_rows)
    pickup_ts = pickup_dates + pd.to_timedelta(pickup_minutes, unit="m")
    trip_distance = rng.gamma(shape=2.5, scale=2.0, size=total_rows)
    fare_amount = trip_distance * 3.2 + rng.normal(2.5, 1.5, size=total_rows)
    zone_ids = np.arange(1, 16)

    df = pd.DataFrame(
        {
            "VendorID": rng.integers(1, 3, size=total_rows),
            "tpep_pickup_datetime": pickup_ts,
            "tpep_dropoff_datetime": pickup_ts + pd.to_timedelta(rng.integers(5, 90, size=total_rows), unit="m"),
            "passenger_count": rng.integers(1, 5, size=total_rows),
            "trip_distance": trip_distance.round(2),
            "fare_amount": fare_amount.round(2),
            "PULocationID": rng.choice(zone_ids, size=total_rows),
            "DOLocationID": rng.choice(zone_ids, size=total_rows),
            "payment_type": rng.integers(1, 5, size=total_rows),
        }
    )
    df["fare_amount"] = df["fare_amount"].clip(lower=2.5)

    support_tables = {
        "taxi_zone_lookup": pd.DataFrame({"LocationID": zone_ids, "Zone": [f"Zone-{idx}" for idx in zone_ids]}),
    }
    return df, support_tables
