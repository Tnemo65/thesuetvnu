"""Range violation injector."""

from __future__ import annotations

from typing import Dict

import pandas as pd

from dqbench.injection.base import FaultInjector, InjectionResult


class RangeViolationInjector(FaultInjector):
    name = "range_violation"

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
        violation_fraction = float(config["severity_map"][severity])
        delta = float(config["delta_map"][severity])
        target_batches = self.pick_target_batches(batch_index, duration, rng)
        direction = str(config.get("violation_direction", "above_max"))
        lower_bound = config.get("min")
        upper_bound = config.get("max")

        modified_rows = 0
        for batch_id in target_batches:
            batch_mask = dirty_df["batch_id"] == batch_id
            batch_indices = dirty_df.loc[batch_mask].index.to_numpy()
            if len(batch_indices) == 0:
                continue
            sample_size = max(1, int(round(len(batch_indices) * violation_fraction)))
            chosen = rng.choice(batch_indices, size=sample_size, replace=False)
            if direction == "below_min":
                base = float(lower_bound if lower_bound is not None else 0.0)
                dirty_df.loc[chosen, target_column] = base - delta
            else:
                base = float(upper_bound if upper_bound is not None else dirty_df[target_column].max())
                dirty_df.loc[chosen, target_column] = base + delta
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
            },
            target_batches=target_batches,
            metadata={
                "target_column": target_column,
                "violation_fraction": violation_fraction,
                "delta": delta,
                "direction": direction,
                "modified_rows": modified_rows,
            },
        )
        return InjectionResult(
            dirty_df=dirty_df,
            dirty_batch_index=self.rebuild_batch_index(dirty_df, batch_index),
            incidents=[incident],
            metadata={"target_batches": list(target_batches)},
        )
