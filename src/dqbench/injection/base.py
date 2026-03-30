"""Base injector abstractions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Sequence

import numpy as np
import pandas as pd

from dqbench.contracts.incidents import IncidentRecord


@dataclass
class InjectionResult:
    dirty_df: pd.DataFrame
    dirty_batch_index: pd.DataFrame
    incidents: List[IncidentRecord]
    metadata: Dict[str, object] = field(default_factory=dict)


class FaultInjector:
    name = "base"

    def inject(
        self,
        clean_df: pd.DataFrame,
        batch_index: pd.DataFrame,
        run_id: str,
        domain: str,
        config: Dict[str, object],
        seed: int,
    ) -> InjectionResult:
        raise NotImplementedError

    @staticmethod
    def _rng(seed: int) -> np.random.Generator:
        return np.random.default_rng(seed)

    @staticmethod
    def duration_to_window_count(duration: str) -> int:
        return 1 if duration == "one_window" else 3

    def pick_target_batches(self, batch_index: pd.DataFrame, duration: str, rng: np.random.Generator) -> Sequence[str]:
        ordered = batch_index.sort_values("batch_order").reset_index(drop=True)
        window_count = self.duration_to_window_count(duration)
        max_start = len(ordered) - window_count
        if max_start < 0:
            raise ValueError("not enough batches to support the requested duration")
        start_idx = int(rng.integers(0, max_start + 1))
        return ordered.loc[start_idx : start_idx + window_count - 1, "batch_id"].tolist()

    @staticmethod
    def rebuild_batch_index(dirty_df: pd.DataFrame, original_batch_index: pd.DataFrame) -> pd.DataFrame:
        counts = dirty_df.groupby("batch_id").size().rename("row_count")
        merged = original_batch_index.drop(columns=["row_count"]).merge(
            counts.reset_index(),
            on="batch_id",
            how="left",
        )
        merged["row_count"] = merged["row_count"].fillna(0).astype(int)
        return merged.sort_values("batch_order").reset_index(drop=True)

    @staticmethod
    def build_incident(
        *,
        incident_id: str,
        run_id: str,
        domain: str,
        family: str,
        severity: str,
        duration: str,
        target_scope: Dict[str, object],
        target_batches: Sequence[str],
        metadata: Dict[str, object],
    ) -> IncidentRecord:
        start_batch = min(target_batches)
        end_batch = max(target_batches)
        return IncidentRecord(
            incident_id=incident_id,
            run_id=run_id,
            domain=domain,
            family=family,
            severity=severity,
            duration=duration,
            target_scope=target_scope,
            start_batch=start_batch,
            end_batch=end_batch,
            window_start=start_batch,
            window_end=end_batch,
            metadata=metadata,
        )
