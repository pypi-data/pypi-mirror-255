import warnings
from typing import Optional

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter


def _colorway() -> list:
    """
    Returns the list of colors from the plotly colorway
    :return: list of colors
    """
    return matplotlib.rcParams["axes.prop_cycle"].by_key()["color"]


def percentage_formatter(x, pos):
    return f"{x*100:.1f}%"


def plot(
    fig: plt.Figure,
    metric: pd.Series,
    cumulative: bool,
    label: str,
    volume: Optional[pd.Series] = None,
    benchmark: Optional[float] = None,
    percent_axis: Optional[bool] = True,
) -> plt.Figure:
    """
    Generates the time series plot
    :param fig: matplotlib figure
    :param metric: series containing the data to plot
    :param cumulative: Whether to plot cumulative or rolling series
    :param label: label for the y axis
    :param volume: series containing the volume to plot
    :param benchmark: benchmark to plot
    :param percent_axis: whether to plot the y axis as percentage
    :return: a matplotlib figure
    """

    if cumulative:
        title = f"Cumulative {label}".title()
    else:
        title = f"Rolling {label}".title()

    ax1 = fig.gca()

    ax1.plot(
        metric.index,
        metric.values,
        color=_colorway()[0],
        markerfacecolor="w",
        marker="o",
        markersize=12,
        lw=2,
        markeredgewidth=4,
        label=title,
    )
    ax1.set_ylabel(title, color=_colorway()[0])

    if volume is not None:
        ax2 = ax1.twinx()
        ax2.plot(
            volume.index,
            volume.values,
            markerfacecolor="w",
            markersize=12,
            lw=2,
            markeredgewidth=4,
            color=_colorway()[1],
            marker="D",
            label="Volume",
            alpha=0.7,
        )
        ax2.set_ylabel("Volume", color=_colorway()[1])
        ax2.spines["right"].set_visible(True)

    if benchmark is not None:
        ax1.axhline(
            benchmark,
            color="red",
            linestyle="--",
            linewidth=2,
            label="Benchmark",
        )

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        if percent_axis:
            ax1.yaxis.set_major_formatter(FuncFormatter(percentage_formatter))

    # set the dates in the x-axis in the format MM-DD
    ax1.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%d-%m"))
    ax1.set_xlabel("Date")
    fig.tight_layout()

    plt.close()

    return fig


def plot_by_primary_channel(
    fig: plt.Figure,
    metric_dic: dict,
    cumulative: bool,
    label: str,
    benchmark: Optional[float] = None,
    percent_axis: Optional[bool] = True,
) -> plt.Figure:
    """
    Generates the time series plot by primary channel
    :param fig: matplotlib figure
    :param metric_dic: dictionary containing the data to plot
    :param cumulative: Whether to plot cumulative or rolling series
    :param label: label for the y axis
    :param benchmark: benchmark to plot
    :param percent_axis: whether to plot the y axis as percentage
    :return: a matplotlib figure
    """

    if cumulative:
        title = f"Cumulative {label}".title()
    else:
        title = f"Rolling {label}".title()

    ax1 = fig.gca()

    for i, (channel, metric) in enumerate(metric_dic.items()):
        ax1.plot(
            metric.index,
            metric.values,
            color=_colorway()[i],
            markerfacecolor="w",
            marker="o",
            markersize=12,
            lw=2,
            markeredgewidth=4,
            label=channel,
        )

    if benchmark is not None:
        ax1.axhline(
            benchmark,
            color="red",
            linestyle="--",
            linewidth=2,
            label="Benchmark",
        )

    ax1.set_ylabel(title)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        if percent_axis:
            ax1.yaxis.set_major_formatter(FuncFormatter(percentage_formatter))

    # set the dates in the x-axis in the format MM-DD
    ax1.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%d-%m"))
    ax1.set_xlabel("Date")

    ax1.legend(frameon=False, loc=(1.05, 0.5))

    fig.tight_layout()

    plt.close()

    return fig
