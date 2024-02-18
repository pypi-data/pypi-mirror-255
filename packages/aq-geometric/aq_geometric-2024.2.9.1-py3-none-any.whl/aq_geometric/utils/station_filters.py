from typing import List

import pandas as pd


def filter_aqsids(
    df: pd.DataFrame,
    measurements_cutoff: int = 20000,
) -> List[str]:
    """Get the list of stations that have more than n measurements."""
    df_aqsid = df[["aqsid", "value"]].groupby("aqsid").count().sort_values(
        "value", ascending=False)
    df_aqsid = df_aqsid[
        df_aqsid["value"] >=
        measurements_cutoff]  # take only aqsids with more than n measurements
    selected_stations = df_aqsid.index.values.tolist()

    return selected_stations
