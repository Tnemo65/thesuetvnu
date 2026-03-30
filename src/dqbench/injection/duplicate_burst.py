"""Duplicate burst injector."""

from __future__ import annotations

from typing import Dict, List

import pandas as pd

from dqbench.injection.base import FaultInjector, InjectionResult


class DuplicateBurstInjector(FaultInjector):
    name = "duplicate_burst"

    def inject(
        self,
        clean_df: pd.DataFrame,
        batch_index: pd.DataFrame,
        run_id: str,
        domain: str,
        config: Dict[str, object],
        seed: int,
    ) -> InjectionResult:
        rng = self._rng(seed)
        dirty_df = clean_df.copy()
        severity = str(config["severity"])
        duration = str(config["duration"])
        duplicate_fraction = float(config["severity_map"][severity])
        target_batches = self.pick_target_batches(batch_index, duration, rng)

        appended_chunks: List[pd.DataFrame] = []
        duplicated_rows = 0
        for batch_id in target_batches:
            batch_df = dirty_df.loc[dirty_df["batch_id"] == batch_id]
            if batch_df.empty:
                continue
            sample_size = max(1, int(round(len(batch_df) * duplicate_fraction)))
            dup_chunk = batch_df.sample(n=sample_size, replace=True, random_state=int(rng.integers(0, 1_000_000)))
            appended_chunks.append(dup_chunk.copy())
            duplicated_rows += len(dup_chunk)
        if appended_chunks:
            dirty_df = pd.concat([dirty_df] + appended_chunks, ignore_index=True)

        incident = self.build_incident(
            incident_id=f"{run_id}:{self.name}",
            run_id=run_id,
            domain=domain,
            family=self.name,
            severity=severity,
            duration=duration,
            target_scope={"level": "table", "ref": config["table_ref"]},
            target_batches=target_batches,
            metadata={"duplicate_fraction": duplicate_fraction, "duplicated_rows": duplicated_rows},
        )
        return InjectionResult(
            dirty_df=dirty_df,
            dirty_batch_index=self.rebuild_batch_index(dirty_df, batch_index),
            incidents=[incident],
            metadata={"target_batches": list(target_batches)},
        )
