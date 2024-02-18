"""
Functions to calculate the total solvency capital.
"""
from typing import Optional

import pandas as pd

from .. import DAY, active_at_t, today
from . import _max_date_range, date_to_period

REQUIRED_COLUMNS = ["sr_scr", "jr_scr", "expired_on", "start", "expiration"]


def current_value(data: pd.DataFrame, **kwargs) -> float:
    """
    Computes the current overall solvency capital.
    """
    mask = active_at_t(data, pd.to_datetime("today"))
    return data.loc[mask].jr_scr.sum() + data.loc[mask].sr_scr.sum()


def at_t(data: pd.DataFrame, date: pd.Timestamp, **kwargs) -> float:
    """
    Computes the solvency capital at time t.
    """
    mask = active_at_t(data, date)
    return data.loc[mask].sr_scr.sum() + data.loc[mask].jr_scr.sum()


def time_series(
    data: pd.DataFrame,
    freq: str = "1W",
    end_date: Optional[pd.Timestamp] = today(),
    start_date: Optional[pd.Timestamp] = today() - 90 * DAY,
    period_column: str = "start",
    **kwargs,
) -> pd.Series:
    """
    Computes the time series of active overall solvency capital locked for the data.
    :param data: policies dataframe.
    :param freq: time series frequency
    :param end_date: maximum date. If None, the maximum date in the period column is used
    :param start_date: minimum date. If None, the minimum date in the period column is used
    :param period_column: can be "start", "expiration", "expired_on", or "max".
    """
    assert "sr_scr" in data.columns, "sr_scr column is required"
    assert "jr_scr" in data.columns, "jr_scr column is required"
    assert "expired_on" in data.columns, "expired_on column is required"
    assert "start" in data.columns, "start column is required"

    if period_column == "max":
        dates = _max_date_range(data=data, freq=freq)
    else:
        dates = sorted(date_to_period(dates=data[period_column], freq=freq).unique())

    scr = []

    get_data = lambda: data[["start", "expired_on", "sr_scr", "jr_scr"]].copy()

    for date in dates:
        scr.append(at_t(get_data(), date))

    scr = pd.Series(scr, index=dates, name="scr")

    if start_date is not None:
        scr = scr.loc[scr.index >= start_date]
    if end_date is not None:
        scr = scr.loc[scr.index <= end_date]

    return scr
