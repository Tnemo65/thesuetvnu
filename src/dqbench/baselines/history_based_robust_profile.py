"""History-Based Robust Profile baseline."""

from __future__ import annotations

from typing import Dict, List

import pandas as pd

from dqbench.baselines.base import DetectorAdapter, infer_scope
from dqbench.data.profiling import numeric_feature_columns

EPS = 1e-6


class HistoryBasedRobustProfileBaseline(DetectorAdapter):
    name = "history_based_robust_profile"

    def __init__(self) -> None:
        self.feature_columns: List[str] = []
        self.history_window: int = 8
        self.table_ref: str = "table"
        self.calibration_tail: pd.DataFrame | None = None

    def fit(self, calibration_profiles: pd.DataFrame, config: Dict[str, object]) -> None:
        self.feature_columns = list(config.get("feature_columns") or numeric_feature_columns(calibration_profiles))
        self.history_window = int(config.get("history_window", 8))
        self.table_ref = str(config.get("table_ref", "table"))
        ordered = calibration_profiles.sort_values("batch_id").reset_index(drop=True)
        self.calibration_tail = ordered.tail(self.history_window).copy()

    def score(self, eval_profiles: pd.DataFrame) -> pd.DataFrame:
        if self.calibration_tail is None:
            raise RuntimeError("fit must be called before score")
        profiles = eval_profiles.sort_values("batch_id").reset_index(drop=True)
        history_source = self.calibration_tail.copy()
        rows = []
        for idx, row in profiles.iterrows():
            history = history_source.tail(self.history_window)[self.feature_columns]
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
            else:
                med = history.median()
                mad = (history - med).abs().median()
                robust_z = (pd.to_numeric(row[self.feature_columns], errors="coerce").fillna(0.0) - med).abs().div(
                    1.4826 * mad + EPS
                )
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
            history_source = pd.concat([history_source, pd.DataFrame([row])], ignore_index=True)
        return pd.DataFrame(rows)
