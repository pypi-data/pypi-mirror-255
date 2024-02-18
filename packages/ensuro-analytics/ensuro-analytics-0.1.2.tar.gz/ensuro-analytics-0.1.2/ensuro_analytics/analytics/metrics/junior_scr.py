"""
Functions to compute the active Junior solvency capital locked.
"""
from typing import Optional

import pandas as pd

from .. import DAY, active_at_t, today
from . import _max_date_range, date_to_period

REQUIRED_COLUMNS = ["jr_scr", "expired_on", "start", "expiration"]


def current_value(data: pd.DataFrame, **kwargs) -> float:
    """
    Computes the current value of the active Junior solvency capital locked
    """
    mask = active_at_t(data, today())
    return data.loc[mask].jr_scr.sum()


def at_t(data: pd.DataFrame, date: pd.Timestamp, **kwargs) -> float:
    """
    Computes the value of the active Junior solvency capital locked at a given date
    """
    mask = active_at_t(data, date)
    return data.loc[mask].jr_scr.sum()


def time_series(
    data: pd.DataFrame,
    freq: str = "1W",
    end_date: Optional[pd.Timestamp] = today(),
    start_date: Optional[pd.Timestamp] = today() - 90 * DAY,
    period_column: str = "start",
    **kwargs,
) -> pd.Series:
    """
    Computes the time series of active Junior solvency capital locked for the data.
    :param data: policies dataframe.
    :param freq: time series frequency
    :param end_date: maximum date. If None, the maximum date in the period column is used
    :param start_date: minimum date. If None, the minimum date in the period column is used
    :param period_column: can be "start", "expiration", "expired_on", or "max".
    """

    if period_column == "max":
        dates = _max_date_range(data=data, freq=freq)
    else:
        dates = sorted(date_to_period(dates=data[period_column], freq=freq).unique())

    jr_scr = []

    get_data = lambda: data[["start", "expired_on", "expiration", "jr_scr"]].copy()

    for date in dates:
        jr_scr.append(at_t(get_data(), date))

    jr_scr = pd.Series(jr_scr, index=dates, name="jr_scr")

    if start_date is not None:
        jr_scr = jr_scr.loc[jr_scr.index >= start_date]
    if end_date is not None:
        jr_scr = jr_scr.loc[jr_scr.index <= end_date]

    return jr_scr
