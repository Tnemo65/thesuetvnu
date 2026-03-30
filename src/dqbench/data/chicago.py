"""Chicago Food Inspections dataset adapter."""

from __future__ import annotations

import pandas as pd

from dqbench.data.base import DatasetAdapter


class ChicagoFoodDatasetAdapter(DatasetAdapter):
    name = "chicago_food"
    timestamp_col = "event_ts"

    def canonicalize(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        rename_map = {"Inspection Date": "event_ts"}
        df = raw_df.rename(columns=rename_map).copy()
        return super().canonicalize(df)
