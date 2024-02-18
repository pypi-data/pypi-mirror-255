"""
Functions to compute the number of active policies
"""
from typing import Optional

import pandas as pd

from .. import DAY, active_at_t, today
from . import _max_date_range, date_to_period

REQUIRED_COLUMNS = ["start", "expired_on", "expiration"]


def current_value(data: pd.DataFrame, **kwargs) -> int:
    """
    Computes the number of active policies at the current date
    """
    mask = active_at_t(data, today())
    return mask.astype(int).sum()


def at_t(data: pd.DataFrame, date: pd.Timestamp, **kwargs) -> int:
    """
    Computes the number of active policies at a given date
    """
    mask = active_at_t(data, date)
    return mask.sum()


def time_series(
    data: pd.DataFrame,
    freq: str = "1W",
    end_date: Optional[pd.Timestamp] = today(),
    start_date: Optional[pd.Timestamp] = today() - 90 * DAY,
    period_column: str = "start",
    **kwargs,
) -> pd.Series:
    """
    Computes the time series of active policies for the data.
    :param data: policies dataframe
    :param freq: time frequency of the time series
    :param end_date: maximum date. If None, the maximum date in the period column is used
    :param start_date: minimum date. If None, the minimum date in the period column is used
    :param period_column: can be "start", "expired_on", "expiration", or "max".
    :return:
    """
    assert "expired_on" in data.columns, "expired_on column is required"
    assert "start" in data.columns, "start column is required"

    # Get unique dates at a regular interval
    if period_column == "max":
        dates = _max_date_range(data=data, freq=freq)
    else:
        dates = sorted(date_to_period(dates=data[period_column], freq=freq).unique())

    active_policies = []
    get_data = lambda: data[["start", "expired_on"]].copy()
    # Compute active policies at each date
    for date in dates:
        active_policies.append(at_t(get_data(), date))

    active_policies = pd.Series(active_policies, index=dates, name="active_policies")

    # Filter by start and end date
    if start_date is not None:
        active_policies = active_policies.loc[active_policies.index >= start_date]
    if end_date is not None:
        active_policies = active_policies.loc[active_policies.index <= end_date]

    return active_policies
