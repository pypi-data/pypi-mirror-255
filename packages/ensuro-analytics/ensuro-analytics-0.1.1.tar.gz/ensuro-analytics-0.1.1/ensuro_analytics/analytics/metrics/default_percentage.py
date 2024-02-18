"""
Functions to compute the default percentage.
"""
from typing import Optional

import numpy as np
import pandas as pd

from .. import DAY, _count_payouts, today
from . import date_to_period

REQUIRED_COLUMNS = ["actual_payout", "start", "expired_on", "expiration"]


def current_value(data: pd.DataFrame, post_mortem: bool = False, **kwargs) -> float:
    """
    Computes the current default percentage
    :param data: policies dataframe
    :param post_mortem: if True, only consider policies with expiration <= today.
    """
    _data = data.copy()
    if post_mortem:
        _data = _data.loc[_data.expiration <= pd.to_datetime("today").normalize()]

    default_percentage = (_data.loc[~_data.actual_payout.isna(), "actual_payout"] > 1e-9).mean()
    default_percentage *= 100

    return default_percentage


def at_t(data: pd.DataFrame, date: pd.Timestamp, post_mortem: bool = False, **kwargs) -> float:
    """
    Computes the default percentage at a given date. If post_mortem is True, only consider policies with
    expiration <= date.
    """
    if post_mortem is True:
        mask = data.expiration <= date
    else:
        mask = np.ones(len(data), dtype=bool)
    # Remove active policies
    mask = mask & ~data.actual_payout.isna()

    # Compute default percentage
    if not any(mask):
        return 0
    x = _count_payouts(data.loc[mask].actual_payout.values) / data.loc[mask].shape[0]

    if np.isnan(x):
        x = 0
    return 100 * x


def time_series(
    data,
    cumulative: bool = False,
    freq: str = "1W",
    end_date: Optional[pd.Timestamp] = today(),
    start_date: Optional[pd.Timestamp] = today() - 90 * DAY,
    period_column: Optional[str] = "expiration",
    percent: Optional[bool] = False,
    **kwargs,
) -> pd.Series:
    """
    Computes data's default percentage time series. Policies are divided in different batches
    based on their expected (period_column = "expiration") or actual (period_column = "expired_on") expiration date.
    For each batch, the function computes policies' default percentage. If cumulative is True, the loss to exposure
    is cumulative.
    :param data: policies dataframe
    :param cumulative: if True, the default percentage is cumulative (i.e., computed on all the policies up to the date)
    :param freq: frequency of the time series
    :param end_date: maximum date. If None, the maximum date in the period column is used
    :param start_date: minimum date. If None, the minimum date in the period column is used
    :param period_column: can be "expired_on", "expiration".
    :param percent: if True, the default percentage is expressed in percentage points
    """
    assert "actual_payout" in data.columns, "actual_payout column is required"
    assert period_column in data.columns, "period column is required"

    data = data[~data[period_column].isna()].copy()

    data["claimed"] = data.actual_payout > 1e-9

    # Transform dates into regular intervals
    data["date"] = date_to_period(dates=data[period_column], freq=freq)

    data = data.groupby("date").agg({"claimed": "sum", "actual_payout": "count"})

    if cumulative:
        data["claimed"] = data.claimed.cumsum()
        data["actual_payout"] = data.actual_payout.cumsum()

    data["default_percentage"] = data.claimed / data.actual_payout
    if not percent:
        data["default_percentage"] *= 100

    if start_date is not None:
        data = data.loc[data.index >= start_date]
    if end_date is not None:
        data = data.loc[data.index <= end_date]
    return data["default_percentage"]


def rolling_at_t(data: pd.DataFrame, date: pd.Timestamp, timedelta=pd.Timedelta(days=7), **kwargs) -> float:
    """
    Computes the default percentage for policies with expiration date in a given time window.
    :param data: policies dataframe
    :param date: center of the time-window
    :param timedelta:  half-width; default is 7 days.
    """
    mask = (data.expiration > date - timedelta) & (data.expiration <= date + timedelta)
    mask = mask & ~data.actual_payout.isna()
    if not any(mask):
        return 0
    x = _count_payouts(data.loc[mask].actual_payout.values) / data.loc[mask].shape[0]
    if np.isnan(x):
        x = 0
    return 100 * x
