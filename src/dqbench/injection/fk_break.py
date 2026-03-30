"""Foreign-key break injector."""

from __future__ import annotations

from typing import Dict

import pandas as pd

from dqbench.injection.base import FaultInjector, InjectionResult


class FKBreakInjector(FaultInjector):
    name = "fk_break"

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
        target_column = str(config["target_column"])
        invalid_fraction = float(config["severity_map"][severity])
        invalid_value = int(config.get("invalid_value", 999999))
        target_batches = self.pick_target_batches(batch_index, duration, rng)

        modified_rows = 0
        for batch_id in target_batches:
            batch_mask = dirty_df["batch_id"] == batch_id
            batch_indices = dirty_df.loc[batch_mask].index.to_numpy()
            if len(batch_indices) == 0:
                continue
            sample_size = max(1, int(round(len(batch_indices) * invalid_fraction)))
            chosen = rng.choice(batch_indices, size=sample_size, replace=False)
            dirty_df.loc[chosen, target_column] = invalid_value
            modified_rows += len(chosen)

        incident = self.build_incident(
            incident_id=f"{run_id}:{self.name}",
            run_id=run_id,
            domain=domain,
            family=self.name,
            severity=severity,
            duration=duration,
            target_scope={
                "level": "column",
                "ref": f"{config['table_ref']}.{target_column}",
                "table_ref": config["table_ref"],
                "relation_ref": config.get("relation_ref", config["table_ref"]),
            },
            target_batches=target_batches,
            metadata={"target_column": target_column, "invalid_fraction": invalid_fraction, "modified_rows": modified_rows},
        )
        return InjectionResult(
            dirty_df=dirty_df,
            dirty_batch_index=self.rebuild_batch_index(dirty_df, batch_index),
            incidents=[incident],
            metadata={"target_batches": list(target_batches)},
        )
