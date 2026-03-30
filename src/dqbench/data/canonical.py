"""Canonical dataframe helpers."""

from __future__ import annotations

import pandas as pd


def assign_daily_batch_id(df: pd.DataFrame, timestamp_col: str) -> pd.DataFrame:
    out = df.copy()
    timestamps = pd.to_datetime(out[timestamp_col], utc=False)
    out["batch_id"] = timestamps.dt.strftime("%Y-%m-%d")
    out["event_date"] = timestamps.dt.normalize()
    return out


def build_batch_index(df: pd.DataFrame, batch_col: str = "batch_id", timestamp_col: str = "event_date") -> pd.DataFrame:
    grouped = (
        df.groupby(batch_col)
        .agg(
            start_time=(timestamp_col, "min"),
            end_time=(timestamp_col, "max"),
            row_count=(batch_col, "size"),
        )
        .reset_index()
        .sort_values(batch_col)
        .reset_index(drop=True)
    )
    grouped["batch_order"] = range(len(grouped))
    grouped["is_missing"] = False
    grouped["is_delayed"] = False
    return grouped
