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
        return 0.0
    if policy == "percentile_90":
        return float(np.quantile(scores.to_numpy(), 0.90))
    if policy == "percentile_95":
        return float(np.quantile(scores.to_numpy(), 0.95))
    if policy == "percentile_99":
        return float(np.quantile(scores.to_numpy(), 0.99))
    raise KeyError(f"Unknown calibration policy {policy!r}")
