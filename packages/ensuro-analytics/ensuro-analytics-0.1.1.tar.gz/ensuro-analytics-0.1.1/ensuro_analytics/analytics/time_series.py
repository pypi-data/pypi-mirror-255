"""
Utils to create time-series data from a table of policies.
"""

import pandas as pd

from .metrics.active_policies import at_t as active_policies_at_t
from .metrics.active_premium import at_t as active_premium_at_t
from .metrics.collected_premium import at_t as won_premium_at_t
from .metrics.collected_premium import rolling_at_t as won_premium_rolling_at_t
from .metrics.default_percentage import at_t as default_percentage_at_t
from .metrics.default_percentage import rolling_at_t as default_percentage_rolling_at_t
from .metrics.loss_ratio import at_t as loss_ratio_at_t
from .metrics.loss_ratio import rolling_at_t as loss_ratio_rolling_at_t
from .metrics.n_payouts import at_t as n_payouts_at_t
from .metrics.payouts import at_t as payout_at_t
from .metrics.post_mortem_premium import at_t as post_mortem_premium_at_t
from .metrics.scr import at_t as scr_at_t
from .metrics.total_policies import at_t as total_policies_at_t
from .metrics.total_policies import rolling_at_t as total_policies_rolling_at_t


def compute_aggregate_metrics(data, date):
    """
    Compute several different analytics metrics at time t.
    """
    active_premium = active_premium_at_t(data, date)
    inactive_premium = won_premium_at_t(data, date)
    active_policies = active_policies_at_t(data, date)
    total_policies = total_policies_at_t(data, date)
    total_payouts = payout_at_t(data, date)
    num_payouts = n_payouts_at_t(data, date)
    total_scr_used = scr_at_t(data, date)
    loss_ratio = loss_ratio_at_t(data, date)
    rolling_loss_ratio = loss_ratio_rolling_at_t(data, date)
    default_percentage = default_percentage_at_t(data, date)
    rolling_default_percentage = default_percentage_rolling_at_t(data, date)
    rolling_n_policies = total_policies_rolling_at_t(data, date)
    rolling_premium = won_premium_rolling_at_t(data, date)
    post_mortem_premium = post_mortem_premium_at_t(data, date)

    results = (
        active_premium,
        inactive_premium,
        active_policies,
        total_policies,
        total_payouts,
        num_payouts,
        total_scr_used,
        loss_ratio,
        rolling_loss_ratio,
        default_percentage,
        rolling_default_percentage,
        rolling_n_policies,
        rolling_premium,
        post_mortem_premium,
    )

    return results


def build_time_series_dataframe(data, freq="1W"):
    """
    Function to aggregate the policy dataset in a time series of metrics. The metrics
    produced are indexed by date/product
    Parameters:
    df (pd.DataFrame): policies dataframe
    risk_module_map (dict): dictionary mapping smart contract addresses to risk modules names
    Returns
    df_ts (pd.DataFrame): dataframe with time series metrics.
    """

    start_date = data.start.min().normalize()
    end_date = pd.to_datetime("today").normalize()

    dates = pd.date_range(start=start_date, end=end_date, normalize=True, freq=freq)
    time_series = pd.DataFrame(dates, columns=["date"])

    get_data = lambda: data.copy()

    # Fill values
    new_columns = [
        "rm_name",
        "active_premium",
        "inactive_premium",
        "active_policies",
        "total_policies",
        "total_payouts",
        "num_payouts",
        "total_scr_used",
        "loss_ratio",
        "rolling_loss_ratio",
        "default_perc",
        "rolling_default_perc",
        "rolling_n_policies",
        "rolling_premium",
        "post_mortem_premium",
    ]

    time_series[new_columns] = pd.DataFrame.from_records(
        time_series["date"].apply((lambda x: compute_aggregate_metrics(get_data(), x)))
    ).values

    return time_series
