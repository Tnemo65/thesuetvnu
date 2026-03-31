"""Isolation Forest baseline using the required scikit-learn backend."""

from __future__ import annotations

from typing import Dict, List

import pandas as pd

from dqbench.baselines.base import DetectorAdapter
from dqbench.data.profiling import numeric_feature_columns

try:
    from sklearn.ensemble import IsolationForest as SKIsolationForest
except Exception:  # pragma: no cover - import error depends on local environment
    SKIsolationForest = None


class IsolationForestBaseline(DetectorAdapter):
    name = "isolation_forest"

    def __init__(self) -> None:
        self.feature_columns: List[str] = []
        self.table_ref: str = "table"
        self.model = None

    def fit(self, calibration_profiles: pd.DataFrame, config: Dict[str, object]) -> None:
        self.feature_columns = list(config.get("feature_columns") or numeric_feature_columns(calibration_profiles))
        self.table_ref = str(config.get("table_ref", "table"))
        if SKIsolationForest is None:
            raise RuntimeError(
                "IsolationForest baseline requires scikit-learn. "
                "Install the project with the 'ml' extra instead of using a fallback detector."
            )
        self.model = SKIsolationForest(
            n_estimators=256,
            max_samples=min(256, len(calibration_profiles)),
            max_features=1.0,
            bootstrap=False,
            contamination="auto",
            random_state=42,
        )
        self.model.fit(calibration_profiles[self.feature_columns])

    def score(self, eval_profiles: pd.DataFrame) -> pd.DataFrame:
        if self.model is None:
            raise RuntimeError("fit must be called before score")
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
