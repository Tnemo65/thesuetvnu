"""NYC 311 dataset adapter."""

from __future__ import annotations

import pandas as pd

from dqbench.data.base import DatasetAdapter


class NYC311DatasetAdapter(DatasetAdapter):
    name = "nyc311"
    timestamp_col = "event_ts"

    def canonicalize(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        rename_map = {"Created Date": "event_ts"}
        df = raw_df.rename(columns=rename_map).copy()
        return super().canonicalize(df)
