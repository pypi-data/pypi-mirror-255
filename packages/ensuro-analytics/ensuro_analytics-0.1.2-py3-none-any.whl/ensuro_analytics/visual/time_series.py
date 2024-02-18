from importlib import import_module
from typing import Optional, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from ..analytics import DAY, _timestamp, today
from ..analytics.metrics.total_policies import time_series as total_policies_time_series
from .matplotlib_layout import time_series as matplotlib_layout
from .plotly_layout import time_series as plotly_layout

AVAILABLE_METRICS = [
    "active_policies",
    "active_premium",
    "collected_premium",
    "default_percentage",
    "junior_scr",
    "loss_ratio",
    "loss_to_exposure",
    "n_payouts",
    "payouts",
    "premium_balance",
    "scr",
    "senior_scr",
    "total_policies",
]

METRICS_PATH = "..analytics.metrics.{}"


def plot(
    data: pd.DataFrame,
    metric: str,
    fig: Union[go.Figure, plt.Figure],
    cumulative: Optional[bool] = True,
    freq: Optional[str] = "1W",
    period_column: Optional[str] = "expiration",
    post_mortem: Optional[bool] = True,
    with_volume: Optional[bool] = True,
    benchmark: Optional[float] = None,
    percent: Optional[bool] = False,
    end_date: Optional[pd.Timestamp] = today(),
    start_date: Optional[pd.Timestamp] = today() - 90 * DAY,
) -> Union[go.Figure, plt.Figure]:
    """
    Generates the metric plot
    :param data: Dataframe containing the data
    :param metric: Metric to plot
    :param fig: Figure object
    :param cumulative: Whether to plot cumulative or rolling loss ratio
    :param freq: Temporal frequency
    :param period_column: Name of the column to use as time
    :param post_mortem: Whether to plot only policies with expiration <= max expired_on
    :param with_volume: Whether to plot volume
    :param benchmark: Benchmark value to plot
    :param percent: Whether to plot as percentage
    :param end_date: End date of the plot
    :param start_date: Start date of the plot
    :return: Plotly or matplotlib figure depending on layout parameter
    """

    assert (
        metric in AVAILABLE_METRICS
    ), f"Metric {metric} not available. Available metrics: {AVAILABLE_METRICS}"

    data = data.copy()

    module = import_module(METRICS_PATH.format(metric), package="ensuro_analytics.visual")

    ts = module.time_series(
        data,
        cumulative=cumulative,
        freq=freq,
        end_date=end_date,
        start_date=start_date,
        period_column=period_column,
        port_mortem=post_mortem,
        percent=True,
    )

    if with_volume:
        volume = total_policies_time_series(
            data,
            cumulative=cumulative,
            freq=freq,
            end_date=end_date,
            start_date=start_date,
            port_mortem=post_mortem,
            period_column=period_column,
        )
    else:
        volume = None

    if isinstance(fig, go.Figure):
        return plotly_layout.plot(
            fig,
            ts,
            cumulative,
            label=metric.replace("_", " "),
            volume=volume,
            benchmark=benchmark,
            percent_axis=percent,
        )
    elif isinstance(fig, plt.Figure):
        return matplotlib_layout.plot(
            fig,
            ts,
            cumulative,
            label=metric.replace("_", " "),
            volume=volume,
            benchmark=benchmark,
            percent_axis=percent,
        )


def plot_by_primary_channel(
    data: pd.DataFrame,
    metric: str,
    fig: Union[go.Figure, plt.Figure],
    primary_channel: Optional[str] = "partner",
    cumulative: Optional[bool] = True,
    freq: Optional[str] = "1W",
    period_column: Optional[str] = "expiration",
    post_mortem: Optional[bool] = True,
    benchmark: Optional[float] = None,
    n_channel: Optional[int] = 5,
    percent: Optional[bool] = False,
    end_date: Optional[pd.Timestamp | str] = today(),
    start_date: Optional[pd.Timestamp | str] = today() - 90 * DAY,
) -> Union[go.Figure, plt.Figure]:
    """
    Generates the metric plot by primary channel
    :param data: Dataframe containing the data
    :param metric: Metric to plot
    :param fig: Figure object
    :param primary_channel: Name of the primary channel column to plot
    :param cumulative: Whether to plot cumulative or rolling loss ratio
    :param freq: Temporal frequency
    :param period_column: Name of the column to use as time
    :param post_mortem: Whether to plot only policies with expiration <= max expired_on
    :param benchmark: Benchmark value to plot
    :param n_channel: Number of channels to plot
    :param percent: Whether to plot as percentage
    :param end_date: End date of the plot
    :param start_date: Start date of the plot
    :return: Plotly or matplotlib figure depending on layout parameter
    """

    assert (
        metric in AVAILABLE_METRICS
    ), f"Metric {metric} not available. Available metrics: {AVAILABLE_METRICS}"

    # Turn start_date and end_date to datetime
    if isinstance(start_date, str):
        start_date = _timestamp(start_date)
    if isinstance(end_date, str):
        end_date = _timestamp(end_date)

    _data = data.copy()

    module = import_module(METRICS_PATH.format(metric), package="ensuro_analytics.visual")

    mask = np.ones(_data.shape[0], dtype=bool)
    if start_date is not None:
        mask &= _data[period_column] >= start_date
    if end_date is not None:
        mask &= _data[period_column] <= end_date

    channels = _data[mask][primary_channel].value_counts().head(n_channel).index
    ts = {}

    for ch in channels:
        ts[ch] = module.time_series(
            _data[_data[primary_channel] == ch],
            cumulative=cumulative,
            freq=freq,
            end_date=end_date,
            start_date=start_date,
            period_column=period_column,
            percent=percent,
            post_mortem=post_mortem,
        )

    if isinstance(fig, go.Figure):
        return plotly_layout.plot_by_primary_channel(
            fig,
            ts,
            cumulative,
            label=metric.replace("_", " "),
            benchmark=benchmark,
            percent_axis=percent,
        )
    elif isinstance(fig, plt.Figure):
        return matplotlib_layout.plot_by_primary_channel(
            fig,
            ts,
            cumulative,
            label=metric.replace("_", " "),
            benchmark=benchmark,
            percent_axis=percent,
        )
