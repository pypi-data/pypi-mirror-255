"""
Functions to compute premium balance.
"""
from typing import Optional

import numpy as np
import pandas as pd

from .. import DAY, today
from . import date_to_period

REQUIRED_COLUMNS = ["premium", "pure_premium", "actual_payout", "expiration", "expired_on", "start"]


def current_value(
    data: pd.DataFrame, post_mortem: bool = False, use_pure_premium: bool = True, **kwargs
) -> float:
    """
    Computes the current premium balance. If post_mortem is True, the premium balance is computed only on
    policies with expiration date <= today. If use_pure_premium is True, the pure premium is used instead of the
    premium.
    :param data: policies dataframe
    :param post_mortem: If True, the premium balance is computed only on policies with expiration date <= today
    :param use_pure_premium: If True, the pure premium is used instead of the premium. Default is True
    """
    _data = data.copy()
    if post_mortem:
        _data = _data.loc[data.expiration <= pd.to_datetime("today").normalize()]
    premium_column = "pure_premium" if use_pure_premium else "premium"
    premium_balance = _data.loc[:, premium_column].sum() - np.nansum(_data.loc[:, "actual_payout"])
    return premium_balance


def at_t(
    data: pd.DataFrame,
    date: pd.Timestamp,
    post_mortem: bool = False,
    use_pure_premium: bool = True,
    **kwargs,
) -> float:
    """
    Computes the premium balance at time t. If post_mortem is True, the premium balance is computed only on
    policies with expiration date <= t. If use_pure_premium is True, the pure premium is used instead of the
    premium.
    :param data: policies dataframe
    :param date: time t
    :param post_mortem: If True, the premium balance is computed only on policies with expiration date <= t
    :param use_pure_premium: If True, the pure premium is used instead of the premium. Default is True
    """
    if use_pure_premium is True:
        premium_column = "pure_premium"
    else:
        premium_column = "premium"

    mask_premium = data.start <= date
    mask_payout = data.expired_on <= date

    if post_mortem is True:
        mask_premium &= data.expiration <= date
        mask_payout &= data.expiration <= date

    premium_balance = (
        data.loc[mask_premium, premium_column].sum() - data.loc[mask_payout].actual_payout.sum()
    )
    return premium_balance


def time_series(
    data,
    cumulative: bool = False,
    freq: str = "1W",
    use_pure_premium: bool = True,
    end_date: Optional[pd.Timestamp] = today(),
    start_date: Optional[pd.Timestamp] = today() - 90 * DAY,
    period_column: str = "expiration",
    **kwargs,
) -> pd.Series:
    """
    Computes the time series of premium balance for the data. Policies are divided in different batches
    based on their expected (period_column = "expiration") or actual (period_column = "expired_on") expiration date.
    For each batch, the function computes policies' premium balance.
    If cumulative is True, the premium balance is cumulative.
    :param data: policies dataframe
    :param cumulative: if True, the premium balance is cumulative (i.e., computed on all the policies up to the date)
    :param freq: frequency of the time series
    :param use_pure_premium: If True, the pure premium is used instead of the premium. Default is True
    :param end_date: maximum date. If None, the maximum date in the period column is used
    :param start_date: minimum date. If None, the minimum date in the period column is used
    :param period_column: column to use for expiration date. It can be "expiration", "expired_on".
    """
    if use_pure_premium is True:
        premium_column = "pure_premium"
    else:
        premium_column = "premium"

    assert premium_column in data.columns, f"{premium_column} column is required"
    assert "actual_payout" in data.columns, "actual_payout column is required"
    assert period_column in data.columns, "expiration column is required"

    _data = data.copy()

    # Transform dates in regular intervals
    _data["date"] = date_to_period(dates=_data[period_column], freq=freq)
    _data = _data.groupby("date").agg({premium_column: "sum", "actual_payout": lambda x: np.nansum(x)})

    if cumulative:
        _data[premium_column] = _data[premium_column].cumsum()
        _data["actual_payout"] = _data.actual_payout.cumsum()

    _data["premium_balance"] = _data[premium_column] - _data["actual_payout"]

    if start_date is not None:
        _data = _data.loc[_data.index >= start_date]
    if end_date is not None:
        _data = _data.loc[_data.index <= end_date]

    return _data["premium_balance"]
