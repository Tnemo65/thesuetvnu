"""EWMA-CUSUM Sequential baseline."""

from __future__ import annotations

from typing import Dict, List

import pandas as pd

from dqbench.baselines.base import DetectorAdapter, infer_scope
from dqbench.data.profiling import numeric_feature_columns

EPS = 1e-6


class EWMACUSUMSequentialBaseline(DetectorAdapter):
    name = "ewma_cusum_sequential"

    def __init__(self) -> None:
        self.feature_columns: List[str] = []
        self.table_ref: str = "table"
        self.lambda_: float = 0.3
        self.k: float = 0.5
        self.medians: pd.Series | None = None
        self.mads: pd.Series | None = None

    def fit(self, calibration_profiles: pd.DataFrame, config: Dict[str, object]) -> None:
        self.feature_columns = list(config.get("feature_columns") or numeric_feature_columns(calibration_profiles))
        self.table_ref = str(config.get("table_ref", "table"))
        self.lambda_ = float(config.get("ewma_lambda", 0.3))
        self.k = float(config.get("cusum_k", 0.5))
        calibration = calibration_profiles[self.feature_columns].apply(pd.to_numeric, errors="coerce").fillna(0.0)
        self.medians = calibration.median()
        self.mads = (calibration - self.medians).abs().median()

    def score(self, eval_profiles: pd.DataFrame) -> pd.DataFrame:
        if self.medians is None or self.mads is None:
            raise RuntimeError("fit must be called before score")

        profiles = eval_profiles.sort_values("batch_id").reset_index(drop=True)
        ewma = pd.Series(0.0, index=self.feature_columns, dtype=float)
        cusum_pos = pd.Series(0.0, index=self.feature_columns, dtype=float)
        cusum_neg = pd.Series(0.0, index=self.feature_columns, dtype=float)
        rows = []

        for _, row in profiles.iterrows():
            values = pd.to_numeric(row[self.feature_columns], errors="coerce").fillna(0.0)
            z = (values - self.medians).div(1.4826 * self.mads + EPS)
            ewma = self.lambda_ * z + (1.0 - self.lambda_) * ewma
            cusum_pos = (cusum_pos + z - self.k).clip(lower=0.0)
            cusum_neg = (cusum_neg - z - self.k).clip(lower=0.0)
            per_feature_score = pd.concat([ewma.abs(), cusum_pos, cusum_neg], axis=1).max(axis=1)
            top_feature = str(per_feature_score.idxmax())
            scope = infer_scope(top_feature, self.table_ref)
            rows.append(
                {
                    "batch_id": row["batch_id"],
                    "score": float(per_feature_score.max()),
                    "top_feature": top_feature,
                    "scope_level": scope["scope_level"],
                    "scope_ref": scope["scope_ref"],
                }
            )

        return pd.DataFrame(rows)
