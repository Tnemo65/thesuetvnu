"""History-based statistical baseline inspired by Redyuk-style monitoring."""

from __future__ import annotations

from typing import Dict, List

import numpy as np
import pandas as pd

from dqbench.baselines.base import DetectorAdapter, infer_scope
from dqbench.data.profiling import numeric_feature_columns


class RedyukHistoryBaseline(DetectorAdapter):
    name = "redyuk_history"

    def __init__(self) -> None:
        self.feature_columns: List[str] = []
        self.history_window: int = 5
        self.table_ref: str = "table"

    def fit(self, calibration_profiles: pd.DataFrame, config: Dict[str, object]) -> None:
        self.feature_columns = list(config.get("feature_columns") or numeric_feature_columns(calibration_profiles))
        self.history_window = int(config.get("history_window", 5))
        self.table_ref = str(config.get("table_ref", "table"))

    def score(self, eval_profiles: pd.DataFrame) -> pd.DataFrame:
        profiles = eval_profiles.sort_values("batch_id").reset_index(drop=True)
        rows = []
        for idx, row in profiles.iterrows():
            history = profiles.loc[max(0, idx - self.history_window) : idx - 1, self.feature_columns]
            if history.empty:
                rows.append(
                    {
                        "batch_id": row["batch_id"],
                        "score": 0.0,
                        "top_feature": "history_warmup",
                        "scope_level": "table",
                        "scope_ref": self.table_ref,
                    }
                )
                continue
            med = history.median()
            mad = (history - med).abs().median().replace(0.0, 1.0)
            robust_z = ((row[self.feature_columns] - med) / mad).abs()
            top_feature = robust_z.idxmax()
            scope = infer_scope(str(top_feature), self.table_ref)
            rows.append(
                {
                    "batch_id": row["batch_id"],
                    "score": float(robust_z.max()),
                    "top_feature": top_feature,
                    "scope_level": scope["scope_level"],
                    "scope_ref": scope["scope_ref"],
                }
            )
        return pd.DataFrame(rows)
