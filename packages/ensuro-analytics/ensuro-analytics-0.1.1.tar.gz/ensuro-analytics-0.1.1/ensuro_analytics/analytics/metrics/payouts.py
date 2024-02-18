"""
Functions to compute payouts.
"""
from typing import Optional

import numpy as np
import pandas as pd

from .. import DAY, today
from . import date_to_period

REQUIRED_COLUMNS = ["actual_payout", "expiration", "expired_on"]


def current_value(data: pd.DataFrame, post_mortem: bool = False, **kwargs) -> float:
    """
    Computes the current overall payouts. If post_mortem is True, the payouts are computed only on
    policies with expiration date <= today.
    """
    _data = data.copy()
    if post_mortem:
        _data = _data.loc[_data.expiration <= pd.to_datetime("today").normalize()]

    payouts = _data.actual_payout.sum()

    return payouts


def at_t(data: pd.DataFrame, date: pd.Timestamp, post_mortem: bool = False, **kwargs) -> float:
    """
    Computes the payouts at time t. If post_mortem is True, the payouts are computed only on
    policies with expiration date <= t.
    """
    if post_mortem is True:
        mask = data.expiration < date
    else:
        mask = np.ones(len(data), dtype=bool)
    mask &= data.expired_on <= date
    return np.nansum(data.loc[mask].actual_payout.values)


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
    Computes the time series of payouts for the data. Policies are divided in different batches
    based on their expected expiration date. For each batch, the function computes the payouts.
    If cumulative is True, the payouts are cumulative.
    :param data: policies dataframe
    :param cumulative: If True, the payouts are cumulative
    :param freq: frequency of the time series
    :param end_date: maximum date of the time series. If None, the maximum expiration date is used
    :param start_date: minimum date of the time series. If None, the minimum expiration date is used
    :param period_column: can be "start", "expired_on", "expiration".
    """
    assert "expiration" in data.columns, "expiration column is required"
    assert "expired_on" in data.columns, "expired_on column is required"
    assert "actual_payout" in data.columns, "actual_payout column is required"

    _data = data.copy()

    # Transform dates into regular intervals
    _data["date"] = date_to_period(dates=_data[period_column], freq=freq)
    _data = _data.groupby("date").agg({"actual_payout": "sum"})

    if cumulative:
        _data["actual_payout"] = _data.actual_payout.cumsum()

    if start_date is not None:
        _data = _data.loc[_data.index >= start_date]
    if end_date is not None:
        _data = _data.loc[_data.index <= end_date]

    return _data["actual_payout"]
