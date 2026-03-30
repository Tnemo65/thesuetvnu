"""Batch-level profiling utilities for detectors and realism validation."""

from __future__ import annotations

from typing import Dict, Iterable, List

import numpy as np
import pandas as pd


def build_batch_profiles(df: pd.DataFrame, dataset_config: Dict[str, object]) -> pd.DataFrame:
    batch_col = str(dataset_config.get("batch_col", "batch_id"))
    duplicate_key = list(dataset_config.get("duplicate_key", []))
    null_columns = list(dataset_config.get("null_columns", []))
    range_columns = dict(dataset_config.get("range_columns", {}))
    fk_columns = dict(dataset_config.get("fk_columns", {}))

    rows: List[Dict[str, object]] = []
    for batch_id, batch_df in df.groupby(batch_col):
        row: Dict[str, object] = {"batch_id": batch_id, "row_count": int(len(batch_df))}

        for column in null_columns:
            row[f"null_ratio__{column}"] = float(batch_df[column].isna().mean()) if column in batch_df else 0.0

        if duplicate_key:
            duplicate_mask = batch_df.duplicated(subset=duplicate_key, keep=False)
            row["duplicate_ratio"] = float(duplicate_mask.mean())
        else:
            row["duplicate_ratio"] = 0.0

        for column, bounds in range_columns.items():
            if column not in batch_df:
                continue
            values = pd.to_numeric(batch_df[column], errors="coerce")
            row[f"min__{column}"] = float(values.min()) if not values.dropna().empty else np.nan
            row[f"max__{column}"] = float(values.max()) if not values.dropna().empty else np.nan
            lower = bounds.get("min")
            upper = bounds.get("max")
            invalid_mask = pd.Series(False, index=batch_df.index)
            if lower is not None:
                invalid_mask = invalid_mask | (values < lower)
            if upper is not None:
                invalid_mask = invalid_mask | (values > upper)
            row[f"range_violation_ratio__{column}"] = float(invalid_mask.mean())

        for column, spec in fk_columns.items():
            valid_values = set(spec.get("valid_values", []))
            if column in batch_df and valid_values:
                row[f"invalid_fk_ratio__{column}"] = float((~batch_df[column].isin(valid_values)).mean())

        rows.append(row)

    profile_df = pd.DataFrame(rows).sort_values("batch_id").reset_index(drop=True)
    return profile_df.fillna(0.0)


def numeric_feature_columns(profile_df: pd.DataFrame) -> List[str]:
    return [
        column
        for column in profile_df.columns
        if column != "batch_id" and pd.api.types.is_numeric_dtype(profile_df[column])
    ]


def summarize_clean_profiles(profile_df: pd.DataFrame, feature_columns: Iterable[str]) -> pd.DataFrame:
    rows = []
    for column in feature_columns:
        series = pd.to_numeric(profile_df[column], errors="coerce").dropna()
        rows.append(
            {
                "feature": column,
                "mean": float(series.mean()) if not series.empty else 0.0,
                "std": float(series.std(ddof=0)) if len(series) > 1 else 0.0,
                "p95": float(series.quantile(0.95)) if not series.empty else 0.0,
                "p99": float(series.quantile(0.99)) if not series.empty else 0.0,
                "max": float(series.max()) if not series.empty else 0.0,
            }
        )
    return pd.DataFrame(rows)
