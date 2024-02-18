"""
Common function for the analytics
"""
from typing import Any

import numpy as np
import pandas as pd

DAY = pd.Timedelta("1D")


def today() -> pd.Timestamp:
    return pd.to_datetime("today").normalize()


def _timestamp(date: Any) -> pd.Timestamp:
    return pd.Timestamp(date).normalize()


def active_at_t(data: pd.DataFrame, date: pd.Timestamp) -> pd.Series:
    mask = data.expired_on.isna() | (data.expired_on > _timestamp(date))
    mask &= data.start <= _timestamp(date)
    return mask


def _between(
    dates: pd.DataFrame,
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
    include_left: bool = True,
    include_right: bool = True,
) -> pd.Series:
    """
    Finds dates between a start and an end date
    :param dates:
    :param start_date:
    :param end_date:
    :param include_left:
    :param include_right:
    :return:
    """
    mask = np.ones(len(dates)).astype(bool)

    if include_left is True:
        mask &= dates >= start_date
    else:
        mask &= dates > start_date

    if include_right is True:
        mask &= dates <= end_date
    else:
        mask &= dates < end_date

    return mask


def expired_between(
    data: pd.DataFrame,
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
    include_left: bool = True,
    include_right: bool = True,
) -> pd.Series:
    """
    Finds policies expired between two dates
    :param data: policies table
    :param start_date:
    :param end_date:
    :param include_left: include start date in the interval
    :param include_right: include end date in the interval
    """

    return _between(
        data.expired_on,
        start_date=start_date,
        end_date=end_date,
        include_left=include_left,
        include_right=include_right,
    )


def started_between(
    data: pd.DataFrame,
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
    include_left: bool = True,
    include_right: bool = True,
) -> pd.Series:
    """
    Finds policies started between two dates
    :param data: policies table
    :param start_date:
    :param end_date:
    :param include_left: include start date in the interval
    :param include_right: include end date in the interval
    """

    return _between(
        data.start,
        start_date=start_date,
        end_date=end_date,
        include_left=include_left,
        include_right=include_right,
    )


def _count_payouts(x):
    return ((~np.isnan(x)) & (x > 1e-9)).sum()


def find_first_date(
    data: pd.DataFrame, splitters=list[str], date_column: str = "start", **kwargs
) -> pd.Series:
    """
    Finds the date of the first policies sold for each of the groups identified by the splitters
    """
    sorted_data = data.copy().sort_values(by=date_column)
    first_dates = sorted_data.groupby(splitters)[date_column].transform("min").dt.date

    return first_dates.reindex(data.index).copy()
