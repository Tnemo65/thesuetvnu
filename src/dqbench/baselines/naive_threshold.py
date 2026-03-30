"""Naive z-score threshold baseline."""

from __future__ import annotations

from typing import Dict, List

import numpy as np
import pandas as pd

from dqbench.baselines.base import DetectorAdapter, infer_scope
from dqbench.data.profiling import numeric_feature_columns


class NaiveThresholdBaseline(DetectorAdapter):
    name = "naive_threshold"

    def __init__(self) -> None:
        self.feature_columns: List[str] = []
        self.means: pd.Series | None = None
        self.stds: pd.Series | None = None
        self.table_ref: str = "table"

    def fit(self, calibration_profiles: pd.DataFrame, config: Dict[str, object]) -> None:
        self.feature_columns = list(config.get("feature_columns") or numeric_feature_columns(calibration_profiles))
        self.table_ref = str(config.get("table_ref", "table"))
        self.means = calibration_profiles[self.feature_columns].mean()
        self.stds = calibration_profiles[self.feature_columns].std(ddof=0).replace(0.0, 1.0)

    def score(self, eval_profiles: pd.DataFrame) -> pd.DataFrame:
        if self.means is None or self.stds is None:
            raise RuntimeError("fit must be called before score")
        zscores = ((eval_profiles[self.feature_columns] - self.means) / self.stds).abs()
        top_feature = zscores.idxmax(axis=1)
        top_score = zscores.max(axis=1)
        rows = []
        for batch_id, feature, score in zip(eval_profiles["batch_id"], top_feature, top_score):
            scope = infer_scope(str(feature), self.table_ref)
            rows.append(
                {
                    "batch_id": batch_id,
                    "score": float(score),
                    "top_feature": feature,
                    "scope_level": scope["scope_level"],
                    "scope_ref": scope["scope_ref"],
                }
            )
        return pd.DataFrame(rows)
