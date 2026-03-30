"""Dataset adapter abstractions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

import pandas as pd

from dqbench.data.canonical import assign_daily_batch_id, build_batch_index


@dataclass
class PreparedDataset:
    canonical_df: pd.DataFrame
    batch_index: pd.DataFrame
    support_tables: Dict[str, pd.DataFrame]


class DatasetAdapter:
    """Base adapter that canonicalizes raw data into a daily-batched table."""

    name: str = "base"
    timestamp_col: str = "event_ts"

    def canonicalize(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """Return a canonicalized dataframe with at least a timestamp column."""
        df = raw_df.copy()
        if self.timestamp_col not in df.columns:
            raise KeyError(f"{self.name} adapter expects timestamp column {self.timestamp_col!r}")
        df[self.timestamp_col] = pd.to_datetime(df[self.timestamp_col], utc=False, errors="coerce")
        df = df.dropna(subset=[self.timestamp_col]).reset_index(drop=True)
        return assign_daily_batch_id(df, self.timestamp_col)

    def prepare(
        self,
        raw_df: pd.DataFrame,
        support_tables: Optional[Dict[str, pd.DataFrame]] = None,
    ) -> PreparedDataset:
        canonical_df = self.canonicalize(raw_df)
        batch_index = build_batch_index(canonical_df)
        return PreparedDataset(
            canonical_df=canonical_df,
            batch_index=batch_index,
            support_tables=support_tables or {},
        )
