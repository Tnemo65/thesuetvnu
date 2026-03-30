"""GE-style representative constraint baseline.

This adapter intentionally stays at the level of representative batch constraints.
It does not claim to be an official Great Expectations execution engine.
"""

from __future__ import annotations

from typing import Dict, List

import pandas as pd

from dqbench.baselines.base import DetectorAdapter, infer_scope


class GreatExpectationsAdapter(DetectorAdapter):
    name = "great_expectations"

    def __init__(self) -> None:
        self.rules: List[Dict[str, object]] = []
        self.table_ref: str = "table"

    def fit(self, calibration_profiles: pd.DataFrame, config: Dict[str, object]) -> None:
        self.rules = list(config.get("expectation_rules", []))
        self.table_ref = str(config.get("table_ref", "table"))

    def score(self, eval_profiles: pd.DataFrame) -> pd.DataFrame:
        rows = []
        for _, row in eval_profiles.iterrows():
            max_violation = 0.0
            top_feature = "table"
            for rule in self.rules:
                feature = str(rule["feature"])
                op = str(rule["op"])
                threshold = float(rule["threshold"])
                value = float(row.get(feature, 0.0))
                violation = 0.0
                if op == "<=" and value > threshold:
                    violation = value - threshold
                elif op == ">=" and value < threshold:
                    violation = threshold - value
                if violation > max_violation:
                    max_violation = violation
                    top_feature = feature
            scope = infer_scope(top_feature, self.table_ref)
            rows.append(
                {
                    "batch_id": row["batch_id"],
                    "score": float(max_violation),
                    "top_feature": top_feature,
                    "scope_level": scope["scope_level"],
                    "scope_ref": scope["scope_ref"],
                }
            )
        return pd.DataFrame(rows)
