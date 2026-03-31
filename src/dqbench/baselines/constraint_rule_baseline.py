"""Constraint-Rule representative baseline."""

from __future__ import annotations

from typing import Dict, List

import pandas as pd

from dqbench.baselines.base import DetectorAdapter, infer_scope

EPS = 1e-6


class ConstraintRuleBaseline(DetectorAdapter):
    name = "constraint_rule_baseline"

    def __init__(self) -> None:
        self.rules: List[Dict[str, object]] = []
        self.table_ref: str = "table"

    def fit(self, calibration_profiles: pd.DataFrame, config: Dict[str, object]) -> None:
        self.table_ref = str(config.get("table_ref", "table"))
        self.rules = []

        for feature in calibration_profiles.columns:
            if feature == "batch_id":
                continue
            if feature == "row_count":
                threshold = float(calibration_profiles[feature].quantile(0.05))
                self.rules.append({"feature": feature, "direction": "lower", "threshold": threshold})
                continue
            if feature == "duplicate_ratio":
                threshold = float(calibration_profiles[feature].quantile(0.95))
                self.rules.append({"feature": feature, "direction": "upper", "threshold": threshold})
                continue
            if feature.startswith("null_ratio__") or feature.startswith("range_violation_ratio__") or feature.startswith(
                "invalid_fk_ratio__"
            ):
                threshold = float(calibration_profiles[feature].quantile(0.95))
                self.rules.append({"feature": feature, "direction": "upper", "threshold": threshold})

    def score(self, eval_profiles: pd.DataFrame) -> pd.DataFrame:
        rows = []
        for _, row in eval_profiles.iterrows():
            max_violation = 0.0
            top_feature = "table"
            for rule in self.rules:
                feature = str(rule["feature"])
                threshold = float(rule["threshold"])
                value = float(row.get(feature, 0.0))
                if rule["direction"] == "lower":
                    violation = max(0.0, threshold - value) / max(abs(threshold), 1.0, EPS)
                else:
                    violation = max(0.0, value - threshold) / max(abs(threshold), 1.0, EPS)
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
