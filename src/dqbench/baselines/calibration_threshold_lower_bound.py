"""Calibration Threshold Lower Bound baseline."""

from __future__ import annotations

from typing import Dict, List

import pandas as pd

from dqbench.baselines.base import DetectorAdapter, infer_scope
from dqbench.data.profiling import numeric_feature_columns

EPS = 1e-6


class CalibrationThresholdLowerBoundBaseline(DetectorAdapter):
    name = "calibration_threshold_lower_bound"

    def __init__(self) -> None:
        self.feature_columns: List[str] = []
        self.medians: pd.Series | None = None
        self.mads: pd.Series | None = None
        self.table_ref: str = "table"

    def fit(self, calibration_profiles: pd.DataFrame, config: Dict[str, object]) -> None:
        self.feature_columns = list(config.get("feature_columns") or numeric_feature_columns(calibration_profiles))
        self.table_ref = str(config.get("table_ref", "table"))
        calibration = calibration_profiles[self.feature_columns].apply(pd.to_numeric, errors="coerce").fillna(0.0)
        self.medians = calibration.median()
        self.mads = (calibration - self.medians).abs().median()

    def score(self, eval_profiles: pd.DataFrame) -> pd.DataFrame:
        if self.medians is None or self.mads is None:
            raise RuntimeError("fit must be called before score")
        eval_numeric = eval_profiles[self.feature_columns].apply(pd.to_numeric, errors="coerce").fillna(0.0)
        robust_scores = (eval_numeric - self.medians).abs().div(1.4826 * self.mads + EPS)
        top_feature = robust_scores.idxmax(axis=1)
        top_score = robust_scores.max(axis=1)
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
