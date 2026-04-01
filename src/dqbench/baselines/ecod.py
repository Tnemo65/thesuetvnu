"""ECOD reference detector adapter using the public PyOD implementation."""

from __future__ import annotations

from typing import Dict, List

import pandas as pd

from dqbench.baselines.base import DetectorAdapter, build_table_level_scores
from dqbench.data.profiling import numeric_feature_columns

try:
    from pyod.models.ecod import ECOD as PyODECOD
except Exception:  # pragma: no cover - import error depends on local environment
    PyODECOD = None


class ECODBaseline(DetectorAdapter):
    name = "ecod"

    def __init__(self) -> None:
        self.feature_columns: List[str] = []
        self.table_ref: str = "table"
        self.model = None

    def fit(self, calibration_profiles: pd.DataFrame, config: Dict[str, object]) -> None:
        self.feature_columns = list(config.get("feature_columns") or numeric_feature_columns(calibration_profiles))
        self.table_ref = str(config.get("table_ref", "table"))
        if PyODECOD is None:
            raise RuntimeError(
                "ECOD reference detector requires PyOD. "
                "Install the project with the 'reference_detectors' extra."
            )
        self.model = PyODECOD(
            contamination=float(config.get("contamination", 0.1)),
            n_jobs=int(config.get("n_jobs", 1)),
        )
        self.model.fit(calibration_profiles[self.feature_columns].to_numpy())

    def score(self, eval_profiles: pd.DataFrame) -> pd.DataFrame:
        if self.model is None:
            raise RuntimeError("fit must be called before score")
        raw_scores = self.model.decision_function(eval_profiles[self.feature_columns].to_numpy())
        return build_table_level_scores(eval_profiles, raw_scores, table_ref=self.table_ref)
