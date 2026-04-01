"""Shared detector baseline API."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, List

import pandas as pd

from dqbench.calibration.policies import threshold_from_policy
from dqbench.contracts.alerts import AlertRecord
from dqbench.contracts.runs import RunSpec


def infer_scope(feature_name: str, default_table_ref: str) -> Dict[str, str]:
    if (
        feature_name.startswith("null_ratio__")
        or feature_name.startswith("range_violation_ratio__")
        or feature_name.startswith("invalid_fk_ratio__")
        or feature_name.startswith("min__")
        or feature_name.startswith("max__")
    ):
        column = feature_name.split("__", 1)[1]
        return {"scope_level": "column", "scope_ref": f"{default_table_ref}.{column}"}
    return {"scope_level": "table", "scope_ref": default_table_ref}


def build_table_level_scores(
    eval_profiles: pd.DataFrame,
    raw_scores: List[float] | pd.Series,
    *,
    table_ref: str,
    top_feature: str = "table_anomaly",
) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "batch_id": eval_profiles["batch_id"],
            "score": pd.Series(raw_scores, index=eval_profiles.index, dtype=float),
            "top_feature": [top_feature] * len(eval_profiles),
            "scope_level": ["table"] * len(eval_profiles),
            "scope_ref": [table_ref] * len(eval_profiles),
        }
    )


class DetectorAdapter(ABC):
    name = "base"

    @abstractmethod
    def fit(self, calibration_profiles: pd.DataFrame, config: Dict[str, object]) -> None:
        raise NotImplementedError

    @abstractmethod
    def score(self, eval_profiles: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError

    def emit_alerts(
        self,
        scores_df: pd.DataFrame,
        calibration_scores: pd.Series,
        run_spec: RunSpec,
        config: Dict[str, object],
    ) -> List[AlertRecord]:
        threshold = threshold_from_policy(calibration_scores, run_spec.calibration_policy, config=config)
        alerts: List[AlertRecord] = []
        for idx, row in scores_df.loc[scores_df["score"] >= threshold].reset_index(drop=True).iterrows():
            alerts.append(
                AlertRecord(
                    alert_id=f"{run_spec.detector}:{run_spec.seed}:{idx}",
                    run_id=build_run_id(run_spec),
                    detector=self.name,
                    domain=run_spec.domain,
                    batch_id=str(row["batch_id"]),
                    scope_level=str(row["scope_level"]),
                    scope_ref=str(row["scope_ref"]),
                    score=float(row["score"]),
                    calibration_policy=run_spec.calibration_policy,
                    payload={"top_feature": row.get("top_feature"), "threshold": threshold},
                )
            )
        return alerts


def build_run_id(run_spec: RunSpec) -> str:
    return ":".join(
        [
            run_spec.domain,
            run_spec.snapshot_id,
            run_spec.fault_family,
            run_spec.severity,
            run_spec.duration,
            run_spec.detector,
            run_spec.calibration_policy,
            str(run_spec.seed),
        ]
    )
