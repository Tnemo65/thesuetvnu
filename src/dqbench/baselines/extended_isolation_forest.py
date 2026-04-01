"""Extended Isolation Forest reference detector adapter using the public eif package."""

from __future__ import annotations

from typing import Dict, List

import pandas as pd

from dqbench.baselines.base import DetectorAdapter, build_table_level_scores
from dqbench.data.profiling import numeric_feature_columns

try:
    from eif import iForest as EIForest
except Exception:  # pragma: no cover - import error depends on local environment
    EIForest = None


class ExtendedIsolationForestBaseline(DetectorAdapter):
    name = "extended_isolation_forest"

    def __init__(self) -> None:
        self.feature_columns: List[str] = []
        self.table_ref: str = "table"
        self.model = None

    def fit(self, calibration_profiles: pd.DataFrame, config: Dict[str, object]) -> None:
        self.feature_columns = list(config.get("feature_columns") or numeric_feature_columns(calibration_profiles))
        self.table_ref = str(config.get("table_ref", "table"))
        if EIForest is None:
            raise RuntimeError(
                "Extended Isolation Forest requires the public 'eif' package. "
                "Install the project with the 'reference_detectors' extra; current builds require Cython<3."
            )
        calibration_matrix = calibration_profiles[self.feature_columns].to_numpy(dtype=float)
        sample_size = min(int(config.get("sample_size_cap", 256)), len(calibration_matrix))
        extension_level = config.get("extension_level", "full")
        if extension_level == "full":
            extension_level = max(len(self.feature_columns) - 1, 0)
        self.model = EIForest(
            calibration_matrix,
            ntrees=int(config.get("ntrees", 256)),
            sample_size=sample_size,
            ExtensionLevel=int(extension_level),
            seed=int(config.get("seed", 42)),
        )

    def score(self, eval_profiles: pd.DataFrame) -> pd.DataFrame:
        if self.model is None:
            raise RuntimeError("fit must be called before score")
        raw_scores = self.model.compute_paths(eval_profiles[self.feature_columns].to_numpy(dtype=float))
        return build_table_level_scores(eval_profiles, raw_scores, table_ref=self.table_ref)
