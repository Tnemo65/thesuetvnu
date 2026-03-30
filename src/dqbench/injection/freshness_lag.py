"""Freshness lag injector."""

from __future__ import annotations

from typing import Dict

import pandas as pd

from dqbench.injection.base import FaultInjector, InjectionResult


class FreshnessLagInjector(FaultInjector):
    name = "freshness_lag"

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
        severity = str(config["severity"])
        duration = str(config["duration"])
        mode = str(config.get("mode", "missing"))
        target_batches = self.pick_target_batches(batch_index, duration, rng)
        dirty_df = clean_df.copy()
        dirty_batch_index = batch_index.copy()

        if mode == "delayed":
            delay_days = int(config.get("delay_days_map", {}).get(severity, 1))
            for batch_id in target_batches:
                mask = dirty_df["batch_id"] == batch_id
                if not mask.any():
                    continue
                dirty_df.loc[mask, "event_date"] = pd.to_datetime(dirty_df.loc[mask, "event_date"]) + pd.Timedelta(days=delay_days)
                dirty_df.loc[mask, "batch_id"] = pd.to_datetime(dirty_df.loc[mask, "event_date"]).dt.strftime("%Y-%m-%d")
                dirty_batch_index.loc[dirty_batch_index["batch_id"] == batch_id, "is_delayed"] = True
            dirty_batch_index = self.rebuild_batch_index(dirty_df, dirty_batch_index)
        else:
            dirty_df = dirty_df.loc[~dirty_df["batch_id"].isin(target_batches)].reset_index(drop=True)
            dirty_batch_index.loc[dirty_batch_index["batch_id"].isin(target_batches), "is_missing"] = True
            dirty_batch_index = self.rebuild_batch_index(dirty_df, dirty_batch_index)

        incident = self.build_incident(
            incident_id=f"{run_id}:{self.name}",
            run_id=run_id,
            domain=domain,
            family=self.name,
            severity=severity,
            duration=duration,
            target_scope={"level": "table", "ref": config["table_ref"]},
            target_batches=target_batches,
            metadata={"mode": mode},
        )
        return InjectionResult(
            dirty_df=dirty_df,
            dirty_batch_index=dirty_batch_index,
            incidents=[incident],
            metadata={"target_batches": list(target_batches)},
        )
