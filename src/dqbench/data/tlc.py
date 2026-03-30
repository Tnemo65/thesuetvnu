"""NYC TLC dataset adapter."""

from __future__ import annotations

import pandas as pd

from dqbench.data.base import DatasetAdapter


class TLCDatasetAdapter(DatasetAdapter):
    name = "tlc"
    timestamp_col = "event_ts"

    def canonicalize(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        rename_map = {"tpep_pickup_datetime": "event_ts"}
        df = raw_df.rename(columns=rename_map).copy()
        return super().canonicalize(df)
