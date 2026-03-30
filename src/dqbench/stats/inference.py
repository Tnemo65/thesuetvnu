"""Inference utilities for benchmark result tables."""

from __future__ import annotations

from itertools import combinations
from typing import Dict, Iterable, Sequence

import numpy as np
import pandas as pd
from scipy.stats import friedmanchisquare, rankdata, wilcoxon


def friedman_test(df: pd.DataFrame, *, condition_col: str, detector_col: str, value_col: str) -> Dict[str, float]:
    pivot = df.pivot_table(index=condition_col, columns=detector_col, values=value_col, aggfunc="mean").dropna()
    if pivot.shape[0] < 2 or pivot.shape[1] < 2:
        raise ValueError("Need at least 2 conditions and 2 detectors for Friedman test")
    statistic, p_value = friedmanchisquare(*[pivot[column].to_numpy() for column in pivot.columns])
    return {"statistic": float(statistic), "p_value": float(p_value), "num_conditions": int(pivot.shape[0])}


def holm_adjust(p_values: Sequence[float]) -> np.ndarray:
    order = np.argsort(p_values)
    adjusted = np.empty(len(p_values), dtype=float)
    prev = 0.0
    m = len(p_values)
    for rank, idx in enumerate(order):
        value = min(1.0, (m - rank) * p_values[idx])
        prev = max(prev, value)
        adjusted[idx] = prev
    return adjusted


def pairwise_wilcoxon_holm(
    df: pd.DataFrame,
    *,
    condition_col: str,
    detector_col: str,
    value_col: str,
) -> pd.DataFrame:
    pivot = df.pivot_table(index=condition_col, columns=detector_col, values=value_col, aggfunc="mean").dropna()
    pairs = []
    p_values = []
    for left, right in combinations(pivot.columns, 2):
        stat, p_value = wilcoxon(pivot[left], pivot[right], zero_method="wilcox", alternative="two-sided")
        pairs.append((left, right, float(stat), float(p_value)))
        p_values.append(float(p_value))
    adjusted = holm_adjust(p_values) if p_values else np.array([])
    return pd.DataFrame(
        [
            {
                "detector_a": left,
                "detector_b": right,
                "statistic": stat,
                "p_value": p_value,
                "p_value_holm": float(adjusted[idx]),
            }
            for idx, (left, right, stat, p_value) in enumerate(pairs)
        ]
    )


def cliffs_delta(x: Iterable[float], y: Iterable[float]) -> float:
    x = list(x)
    y = list(y)
    greater = 0
    lower = 0
    for xi in x:
        for yi in y:
            if xi > yi:
                greater += 1
            elif xi < yi:
                lower += 1
    denom = len(x) * len(y)
    return 0.0 if denom == 0 else (greater - lower) / denom


def vargha_delaney_a12(x: Iterable[float], y: Iterable[float]) -> float:
    x = np.asarray(list(x), dtype=float)
    y = np.asarray(list(y), dtype=float)
    if len(x) == 0 or len(y) == 0:
        return 0.5
    combined = np.concatenate([x, y])
    ranks = rankdata(combined)
    r1 = np.sum(ranks[: len(x)])
    return float((r1 / len(x) - (len(x) + 1) / 2.0) / len(y))
