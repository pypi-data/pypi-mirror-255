"""
Functions to compute the premium of active policies
"""
from typing import Optional

import pandas as pd

from .. import DAY, active_at_t, today
from . import _max_date_range, date_to_period

REQUIRED_COLUMNS = ["premium", "expired_on", "start"]


def current_value(data: pd.DataFrame, **kwargs) -> float:
    """
    Computes the current value of the active premium
    """
    mask = active_at_t(data, today())
    return data.loc[mask].premium.sum()


def at_t(data: pd.DataFrame, date: pd.Timestamp, **kwargs) -> float:
    """
    Computes the value of the active premium at a given date
    """
    mask = active_at_t(data, date)
    return data.loc[mask].premium.sum()


def time_series(
    data: pd.DataFrame,
    freq: str = "1W",
    end_date: Optional[pd.Timestamp] = today(),
    start_date: Optional[pd.Timestamp] = today() - 90 * DAY,
    period_column: str = "start",
    **kwargs,
) -> pd.Series:
    """
    Computes the time series of active premium for the data.
    :param data: policies dataframe
    :param freq: time frequency of the time series
    :param end_date: maximum date. If None, the maximum date in the period column is used
    :param start_date: minimum date. If None, the minimum date in the period column is used
    :param period_column: can be "start", "expired_on", "expiration", or "max".
    """
    assert "premium" in data.columns, "premium column is required"
    assert "expired_on" in data.columns, "expired_on column is required"
    assert "start" in data.columns, "start column is required"

    if period_column == "max":
        dates = _max_date_range(data=data, freq=freq)
    else:
        dates = sorted(date_to_period(dates=data[period_column], freq=freq).unique())

    active_premiums = []

    get_data = lambda: data[["start", "expired_on", "premium"]].copy()

    for date in dates:
        active_premiums.append(at_t(get_data(), date))

    active_premiums = pd.Series(active_premiums, index=dates, name="active_premiums")

    if start_date is not None:
        active_premiums = active_premiums.loc[active_premiums.index >= start_date]
    if end_date is not None:
        active_premiums = active_premiums.loc[active_premiums.index <= end_date]

    return active_premiums
