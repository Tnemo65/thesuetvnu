"""Aggregate run metrics into tabular summaries."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

import pandas as pd


def collect_metric_records(output_root: str | Path) -> pd.DataFrame:
    records: List[dict] = []
    for path in Path(output_root).rglob("metrics.json"):
        record = json.loads(path.read_text())
        record["run_dir"] = str(path.parent)
        record["run_name"] = path.parent.name
        records.append(record)
    if not records:
        return pd.DataFrame()
    return pd.DataFrame(records)


def summarize_metrics(df: pd.DataFrame, metric_columns: List[str]) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    available = [column for column in metric_columns if column in df.columns]
    summary = df[available].agg(["mean", "median", "min", "max"]).transpose().reset_index()
    return summary.rename(columns={"index": "metric"})
