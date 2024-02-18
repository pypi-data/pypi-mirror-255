"""
Functions to compute the collected premium.
"""
from typing import Optional

import pandas as pd

from .. import DAY, active_at_t, today
from . import _max_date_range, date_to_period

REQUIRED_COLUMNS = ["premium", "start", "expired_on"]


def current_value(data: pd.DataFrame, **kwargs) -> float:
    """
    Computes the current value of the collected premium
    """
    mask = active_at_t(data, pd.to_datetime("today"))
    return data.loc[~mask].premium.sum()


def at_t(data: pd.DataFrame, date: pd.Timestamp, **kwargs) -> float:
    """
    Computes the value of the collected premium at a given date
    """
    mask = (~data.expired_on.isna()) & (data.expired_on < date)
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
    Computes the time series of the collected ("won") premiums at a given date.
    :param data: policies dataframe
    :param freq: time frequency of the time series
    :param end_date: maximum date. If None, the maximum date in the period column is used
    :param start_date: minimum date. If None, the minimum date in the period column is used
    :param period_column: can be "start", "expired_on", "expiration", or "max".
    """
    assert "premium" in data.columns, "premium column is required"
    assert period_column in data.columns, f"{period_column} column is required"
    assert "expired_on" in data.columns, "expired_on column is required"

    if period_column == "max":
        dates = _max_date_range(data=data, freq=freq)
    else:
        dates = sorted(date_to_period(dates=data[period_column], freq=freq).unique())

    inactive_premiums = []

    get_data = lambda: data[["expired_on", "premium"]].copy()

    for date in dates:
        inactive_premiums.append(at_t(get_data(), date))

    inactive_premiums = pd.Series(inactive_premiums, index=dates, name="collected_premiums")

    if start_date is not None:
        inactive_premiums = inactive_premiums.loc[inactive_premiums.index >= start_date]
    if end_date is not None:
        inactive_premiums = inactive_premiums.loc[inactive_premiums.index <= end_date]

    return inactive_premiums


def rolling_at_t(data: pd.DataFrame, date: pd.Timestamp, timedelta=pd.Timedelta(days=7)):
    """
    Computes the value of the collected premium for policies expired in a given time window.
    :param data: policies dataframe
    :param date: center of the time window
    :param timedelta: half-width of the time window; default is 7 days.
    """
    data = data.loc[~data.expired_on.isna()]
    mask = (data.expired_on > date - timedelta) & (data.expired_on <= date + timedelta)
    return data.loc[mask].pure_premium.sum()
