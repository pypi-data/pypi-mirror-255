"""
Functions to compute the loss ratio.
"""
from typing import Optional

import numpy as np
import pandas as pd

from .. import DAY, today
from . import date_to_period

REQUIRED_COLUMNS = ["pure_premium", "actual_payout", "expiration", "expired_on"]


def current_value(data: pd.DataFrame, post_mortem: bool = False, **kwargs) -> float:
    """
    Computes the current loss ratio. If post_mortem is True, the loss ratio is computed only on policies with expiration
    date <= today.
    """
    _data = data.copy()
    if post_mortem:
        _data = _data.loc[data.expiration <= pd.to_datetime("today").normalize()]
    loss_ratio = _data.actual_payout.sum() / _data.pure_premium.sum() * 100
    return loss_ratio


def at_t(data: pd.DataFrame, date: pd.Timestamp, post_mortem: bool = False, **kwargs) -> float:
    """
    Computes the loss ratio at time t. If post_mortem is True, the loss ratio is computed only on policies with
    expiration date <= t.
    """

    if post_mortem is True:
        mask = data.expiration < date
    else:
        mask = np.ones(len(data), dtype=bool)
    # Remove active policies
    mask &= ~data.actual_payout.isna()

    if not any(mask.values):
        return 0
    # Compute loss ratio
    x = data.loc[mask].actual_payout.sum() / data.loc[mask].pure_premium.sum()
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
    Computes data's loss ratio time series. Policies are divided in different batches
    based on their expected (period_column = "expiration") or actual (period_column = "expired_on") expiration date.
    For each batch, the function computes policies' default percentage. If cumulative is True, the loss ratio
    is cumulative.
    :param data: policies dataframe
    :param cumulative: if True, the loss ratio is cumulative (i.e., computed on all the policies up to the date)
    :param freq: frequency of the time series
    :param end_date: maximum date. If None, the maximum date in the period column is used
    :param start_date: minimum date. If None, the minimum date in the period column is used,
    :param period_column: can be "expiration", "expired_on".
    :param percent: if True, the loss ratio is expressed as a percentage
    """
    assert "pure_premium" in data.columns, "pure_premium column is required"
    assert "actual_payout" in data.columns, "actual_payout column is required"
    assert period_column in data.columns, "period column is required"

    data = data[~data[period_column].isna()].copy()

    data["date"] = date_to_period(dates=data[period_column], freq=freq)
    data = data.groupby("date").agg({"pure_premium": "sum", "actual_payout": "sum"})

    if cumulative:
        data["pure_premium"] = data.pure_premium.cumsum()
        data["actual_payout"] = data.actual_payout.cumsum()

    data["loss_ratio"] = data.actual_payout / data.pure_premium
    if not percent:
        data["loss_ratio"] *= 100

    if start_date is not None:
        data = data.loc[data.index >= start_date]
    if end_date is not None:
        data = data.loc[data.index <= end_date]
    return data["loss_ratio"]


def rolling_at_t(data, date, timedelta=pd.Timedelta(days=7)) -> float:
    """
    Computes the loss ratio of the policies with expiration date in a given time window.
    :param data: policies dataframe
    :param date: center of the time window
    :param timedelta: half-width of the time window
    """
    mask = (data.expiration > date - timedelta) & (data.expiration <= date + timedelta)
    mask = mask & ~data.actual_payout.isna()
    x = data.loc[mask].actual_payout.sum() / data.loc[mask].pure_premium.sum()
    if np.isnan(x):
        x = 0
    return 100 * x
