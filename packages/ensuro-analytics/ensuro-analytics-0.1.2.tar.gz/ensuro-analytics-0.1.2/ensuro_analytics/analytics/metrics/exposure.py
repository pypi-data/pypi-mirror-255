"""
Functions to compute exposure.
"""
from typing import Optional

import pandas as pd

from .. import DAY, active_at_t, today
from . import _max_date_range, date_to_period

REQUIRED_COLUMNS = ["payout", "start", "expiration", "expired_on"]


def current_value(data: pd.DataFrame, **kwargs) -> float:
    """
    Computes the current exposure.
    """
    mask = active_at_t(data, today())
    return data.loc[mask].payout.sum()


def at_t(data: pd.DataFrame, date: pd.Timestamp, **kwargs) -> float:
    """
    Computes the exposure at time t.
    """
    mask = active_at_t(data, date)
    return data.loc[mask].payout.sum()


def time_series(
    data: pd.DataFrame,
    freq: str = "1W",
    end_date: Optional[pd.Timestamp] = today(),
    start_date: Optional[pd.Timestamp] = today() - 90 * DAY,
    period_column: str = "start",
    **kwargs,
) -> pd.Series:
    """
    Computes the time series of exposure for the data.
    :param data: policies dataframe
    :param freq: time frequency of the time series
    :param end_date: maximum date. If None, the maximum date in the period column is used
    :param start_date: minimum date. If None, the minimum date in the period column is used
    :param period_column: can be "start", "expired_on",  "expiration", or "max".
    :return:
    """
    assert "expired_on" in data.columns, "expired_on column is required"
    assert "start" in data.columns, "start column is required"

    # Get unique dates at a regular interval
    if period_column == "max":
        dates = _max_date_range(data=data, freq=freq)
    else:
        dates = sorted(date_to_period(dates=data[period_column], freq=freq).unique())

    exposure = []
    get_data = lambda: data[["start", "expired_on", "payout"]].copy()
    # Compute active policies at each date
    for date in dates:
        exposure.append(at_t(get_data(), date))

    exposure = pd.Series(exposure, index=dates, name="exposure")

    # Filter by start and end date
    if start_date is not None:
        exposure = exposure.loc[exposure.index >= start_date]
    if end_date is not None:
        exposure = exposure.loc[exposure.index <= end_date]

    return exposure
