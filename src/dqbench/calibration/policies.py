"""Score calibration helpers."""

from __future__ import annotations

import math
from typing import Dict

import numpy as np
import pandas as pd


def threshold_from_policy(scores: pd.Series, policy: str, config: Dict[str, float] | None = None) -> float:
    config = config or {}
    scores = pd.to_numeric(scores, errors="coerce").fillna(0.0)
    if scores.empty:
        return float(config.get("static_threshold", 0.0))
    if policy == "static":
        return float(config.get("static_threshold", 3.0))
    if policy == "percentile_95":
        return float(np.quantile(scores.to_numpy(), 0.95))
    if policy == "alert_budget_5pct":
        top_k = max(1, int(math.ceil(len(scores) * 0.05)))
        ordered = np.sort(scores.to_numpy())
        return float(ordered[-top_k])
    raise KeyError(f"Unknown calibration policy {policy!r}")
