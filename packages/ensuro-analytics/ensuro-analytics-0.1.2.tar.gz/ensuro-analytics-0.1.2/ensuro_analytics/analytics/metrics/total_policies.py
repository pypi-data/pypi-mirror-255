"""
Functions to compute the overall number of policies sold.
"""
from typing import Optional

import pandas as pd

from .. import DAY, _timestamp, started_between, today
from . import date_to_period

REQUIRED_COLUMNS = ["expiration", "start", "pure_premium", "premium"]


def current_value(data, post_mortem: bool = False, **kwargs) -> int:
    """
    Computes the total number of policies sold. If post_mortem is True, the number of policies sold is computed only on
    policies with expiration date <= today.
    """
    _data = data.copy()
    if post_mortem:
        _data = _data.loc[_data.expiration <= pd.to_datetime("today").normalize()]

    return _data.shape[0]


def at_t(data: pd.DataFrame, date: pd.Timestamp, post_mortem: bool = False, **kwargs) -> int:
    """
    Computes the number of policies sold at time t. If post_mortem is True, the number of policies sold is computed only on
    policies with expiration date <= t.
    """
    mask = data.start <= _timestamp(date)
    if post_mortem:
        mask &= data.expiration <= _timestamp(date)
    return mask.sum()


def time_series(
    data: pd.DataFrame,
    freq: str = "1W",
    cumulative: bool = False,
    end_date: Optional[pd.Timestamp] = today(),
    start_date: Optional[pd.Timestamp] = today() - 90 * DAY,
    period_column: str = "start",
    **kwargs,
) -> pd.Series:
    """
    Computes the time series of number of policies sold for the data. Policies are divided in different batches
    based on their start date. For each batch, the function computes the number of policies sold.
    If cumulative is True, the number of policies sold is cumulative.
    :param data: policies dataframe
    :param freq: frequency of the time series
    :param cumulative: If True, the number of policies sold is cumulative
    :param end_date: maximum date of the time series. If None, the maximum date in period column is used
    :param start_date: minimum date of the time series. If None, the minimum date in period column is used
    :param period_column: column used to group policies. Can be "start", "expired_on", "expiration".
    """
    _data = data.copy()
    _data["date"] = date_to_period(dates=_data[period_column], freq=freq)
    _data = (
        _data.groupby("date")
        .agg({"pure_premium": "count"})
        .rename(columns={"pure_premium": "total_policies"})
    )

    if cumulative is True:
        _data["total_policies"] = _data["total_policies"].cumsum()

    if start_date is not None:
        _data = _data.loc[_data.index >= start_date]
    if end_date is not None:
        _data = _data.loc[_data.index <= end_date]

    return _data["total_policies"]


def rolling_at_t(data: pd.DataFrame, date: pd.Timestamp, timedelta=pd.Timedelta(days=7), **kwargs) -> int:
    """
    Computes the number of policies sold in a given time window.
    :param data: policies dataframe
    :param date: time window center
    :param timedelta: half-width of the time window
    """
    start_date = date - timedelta
    end_date = date + timedelta
    mask = started_between(data, start_date=start_date, end_date=end_date)
    return mask.sum()
