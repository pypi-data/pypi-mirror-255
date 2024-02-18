"""
Functions to compute the number of payouts.
"""
from typing import Optional

import numpy as np
import pandas as pd

from .. import DAY, _count_payouts, today
from . import date_to_period

REQUIRED_COLUMNS = ["actual_payout", "start", "expiration", "expired_on"]


def current_value(data: pd.DataFrame, post_mortem: bool = False, **kwargs) -> float:
    """
    Computes the current overall number of payouts. If post_mortem is True, the number of payouts is computed only on
    policies with expiration date <= today.
    """
    _data = data.copy()
    if post_mortem:
        _data = _data.loc[_data.expiration <= pd.to_datetime("today").normalize()]

    n_payouts = (_data.actual_payout > 1e-9).sum()

    return n_payouts


def at_t(data: pd.DataFrame, date: pd.Timestamp, post_mortem: bool = False, **kwargs) -> float:
    """
    Computes the number of payouts at time t. If post_mortem is True, the number of payouts is computed only on
    policies with expiration date <= t.
    """
    if post_mortem is True:
        mask = data.expiration < date
    else:
        mask = np.ones(len(data), dtype=bool)

    mask &= data.expired_on <= date
    return (data.loc[mask].actual_payout > 1e-9).sum()


def time_series(
    data: pd.DataFrame,
    cumulative: bool = False,
    freq: str = "1W",
    end_date: Optional[pd.Timestamp] = today(),
    start_date: Optional[pd.Timestamp] = today() - 90 * DAY,
    period_column: Optional[str] = "expiration",
    **kwargs,
) -> pd.Series:
    """
    Computes the time series of number of payouts for the data. Policies are divided in different batches
    based on their expected expiration date. For each batch, the function computes the number of payouts.
    If cumulative is True, the number of payouts is cumulative.
    :param data: policies dataframe
    :param cumulative: If True, the number of payouts is cumulative
    :param freq: frequency of the time series
    :param end_date: maximum date of the time series. If None, the maximum expiration date is used
    :param start_date: minimum date of the time series. If None, the minimum expiration date is used
    :param period_column: can be "start", "expired_on", "expiration".
    """
    assert "actual_payout" in data.columns, "actual_payout column is required"
    assert "start" in data.columns, "start column is required"
    assert "expired_on" in data.columns, "expired_on column is required"

    _data = data.copy()

    # Find first day of expiration week
    _data["date"] = date_to_period(dates=_data[period_column], freq=freq)

    _data = (
        _data.groupby("date")
        .agg({"actual_payout": _count_payouts})
        .rename(columns={"actual_payout": "n_payout"})
    )

    if cumulative:
        _data["n_payout"] = _data.n_payout.cumsum()

    if start_date is not None:
        _data = _data.loc[_data.index >= start_date]
    if end_date is not None:
        _data = _data.loc[_data.index <= end_date]

    return _data["n_payout"]
