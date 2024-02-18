"""
This module contains functions to compute post mortem premium.
"""
import warnings

import pandas as pd

REQUIRED_COLUMNS = ["expiration", "pure_premium"]


def current_value(data: pd.DataFrame, **kwargs) -> float:
    """
    Computes the current overall post mortem premium.
    """
    return at_t(
        data,
        pd.to_datetime("today"),
    )


def at_t(data: pd.DataFrame, date: pd.Timedelta, **kwargs) -> float:
    """
    Computes the post mortem premium at time t.
    """
    mask = data.expiration < date
    return data.loc[mask].pure_premium.sum()


# TODO: scrivere questa funzione
def time_series(data, freq="1W", end_date="today", **kwargs):
    """
    Computes the time series of post mortem premium for the data. Policies are divided in different batches
    based on their expected expiration date. For each batch, the function computes the post mortem premium.
    """
    warnings.warn(
        "post_mortem_premium.time_series not implemented",
        UserWarning,
    )
    pass
