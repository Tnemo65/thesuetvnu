"""Isolation Forest baseline with optional sklearn backend."""

from __future__ import annotations

from typing import Dict, List

import numpy as np
import pandas as pd

from dqbench.baselines.base import DetectorAdapter
from dqbench.baselines.naive_threshold import NaiveThresholdBaseline
from dqbench.data.profiling import numeric_feature_columns

try:
    from sklearn.ensemble import IsolationForest as SKIsolationForest
except Exception:  # pragma: no cover - exercised by fallback path on machines without sklearn
    SKIsolationForest = None


class IsolationForestBaseline(DetectorAdapter):
    name = "isolation_forest"

    def __init__(self) -> None:
        self.feature_columns: List[str] = []
        self.table_ref: str = "table"
        self.model = None
        self.fallback = NaiveThresholdBaseline()

    def fit(self, calibration_profiles: pd.DataFrame, config: Dict[str, object]) -> None:
        self.feature_columns = list(config.get("feature_columns") or numeric_feature_columns(calibration_profiles))
        self.table_ref = str(config.get("table_ref", "table"))
        if SKIsolationForest is None:
            self.fallback.fit(calibration_profiles, config)
            self.model = None
            return
        self.model = SKIsolationForest(
            n_estimators=int(config.get("n_estimators", 100)),
            contamination=float(config.get("contamination", 0.05)),
            random_state=int(config.get("random_state", 42)),
        )
        self.model.fit(calibration_profiles[self.feature_columns])

    def score(self, eval_profiles: pd.DataFrame) -> pd.DataFrame:
        if self.model is None:
            return self.fallback.score(eval_profiles)
        raw_scores = -self.model.decision_function(eval_profiles[self.feature_columns])
        return pd.DataFrame(
            {
                "batch_id": eval_profiles["batch_id"],
                "score": raw_scores.astype(float),
                "top_feature": ["table_anomaly"] * len(eval_profiles),
                "scope_level": ["table"] * len(eval_profiles),
                "scope_ref": [self.table_ref] * len(eval_profiles),
            }
        )
