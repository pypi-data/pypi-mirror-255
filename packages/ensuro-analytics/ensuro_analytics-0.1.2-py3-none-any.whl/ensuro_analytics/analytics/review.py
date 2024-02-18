"""
Portfolio review
"""
import itertools
import warnings
from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd

from . import active_at_t, find_first_date, today
from .metrics import loss_ratio, loss_to_exposure


@dataclass
class PortfolioReview:
    """
    A class used to review a portfolio of insurance policies.

    ...

    Attributes
    ----------
    data : pd.DataFrame
        a pandas DataFrame containing the policies data
    split_on : list[str]
        a list of columns to split the portfolio on

    Methods
    -------
    from_data(data: pd.DataFrame, split_on: str | list[str] = ["rm_name"]) -> "PortfolioReview":
        Creates a PortfolioReview object from a dataframe.
    _validate_data(data: pd.DataFrame, cols: Optional[list[str]] = None):
        Validates the data
    review(show_first_date: bool = True, show_predicted_loss_to_exposure: bool = True, show_current_portfolio_pct: bool = True, **kwargs) -> "_CompiledReview":
        Computes the portfolio review
    """

    data: pd.DataFrame
    split_on: list[str]

    @classmethod
    def from_data(
        cls,
        data: pd.DataFrame,
        split_on: str | list[str] = ["rm_name"],
        validate_columns: Optional[list[str]] = None,
    ) -> "PortfolioReview":
        """
        Creates a PortfolioReview object from a dataframe.

        Parameters
        ----------
        data : pd.DataFrame
            policies dataframe
        split_on : str | list[str]
            list of columns to split the portfolio on
        validate_columns : Optional[list[str]]
            list of columns that the data should have; standard policies columns are validated by default.

        Returns
        -------
        PortfolioReview
            a PortfolioReview object
        """

        cls._validate_data(data, cols=validate_columns)
        if isinstance(split_on, str):
            split_on = [split_on]

        return cls(
            data=data,
            split_on=split_on,
        )

    @staticmethod
    def _validate_data(data: pd.DataFrame, cols: Optional[list[str]] = None):
        """
        Validates the data

        Parameters
        ----------
        data : pd.DataFrame
            policies dataframe
        cols : Optional[list[str]]
            list of columns to validate
        """
        assert "expired_on" in data.columns, "expired_on column is required"
        assert "start" in data.columns, "start column is required"
        assert "expiration" in data.columns, "expiration column is required"
        assert "pure_premium" in data.columns, "pure_premium column is required"
        assert "payout" in data.columns, "payout column is required"
        assert "actual_payout" in data.columns, "actual_payout column is required"

        if cols is not None:
            for col in cols:
                assert col in data.columns, f"{col} column is required"

    def review(
        self,
        show_first_date: bool = True,
        show_predicted_loss_to_exposure: bool = True,
        show_current_portfolio_pct: bool = True,
        **kwargs,
    ) -> "_CompiledReview":
        """
        Computes the portfolio review

        Parameters
        ----------
        show_first_date : bool
            whether to show the first date in the review
        show_predicted_loss_to_exposure : bool
            whether to show the predicted loss to exposure in the review
        show_current_portfolio_pct : bool
            whether to show the current portfolio percentage in the review
        **kwargs
            arbitrary keyword arguments

        Returns
        -------
        _CompiledReview
            a compiled review object
        """

        records = []

        pm_mask = np.ones(self.data.shape[0], dtype=bool)
        pm_mask &= self.data.expiration < today()

        active_mask = active_at_t(self.data, today())

        splitters = [self.data[col].unique() for col in self.split_on]

        if show_first_date:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                first_dates = find_first_date(self.data, self.split_on, **kwargs)
                self.data.loc[:, "first_date"] = first_dates

        for split in itertools.product(*splitters):
            mask = np.ones(self.data.shape[0], dtype=bool)
            for col, value in zip(self.split_on, split):
                mask &= self.data[col] == value

            if (mask & pm_mask).sum() > 0:
                if show_current_portfolio_pct:
                    # Compute incidence of the segment on the current portfolio
                    portfolio_pct = (
                        self.data.loc[active_mask & mask, "payout"].copy().sum()
                        / self.data.loc[active_mask, "payout"].copy().sum()
                        * 100
                    )

                # From here on, only work post-mortem
                mask = mask & pm_mask
                record = [*split]

                if show_first_date:
                    record.append(self.data.loc[mask].first_date.min())

                if show_predicted_loss_to_exposure:
                    record.append(
                        self.data.loc[mask].pure_premium.sum() / self.data.loc[mask].payout.sum() * 100
                    )

                record += [
                    loss_to_exposure.current_value(self.data.loc[mask]),
                    loss_ratio.current_value(self.data.loc[mask]),
                    mask.sum(),
                ]

                if show_current_portfolio_pct:
                    record.append(portfolio_pct)

                records.append(tuple(record))

        columns = [x for x in self.split_on]

        if show_first_date:
            columns += ["first_date"]
        if show_predicted_loss_to_exposure:
            columns += ["pred_loss_to_exposure"]

        columns += ["loss_to_exposure", "loss_ratio", "volume"]

        if show_current_portfolio_pct:
            columns += ["current_pct"]

        results = pd.DataFrame.from_records(records, columns=columns)
        results = results.sort_values(by=self.split_on).set_index(self.split_on)

        return _CompiledReview(results)


@dataclass
class _CompiledReview:
    """
    A class used to compile and represent the results of a portfolio review.

    ...

    Attributes
    ----------
    portfolio_review : pd.DataFrame
        a pandas DataFrame containing the results of the portfolio review

    Methods
    -------
    to_df() -> pd.DataFrame:
        Returns a copy of the portfolio review results as a pandas DataFrame.
    to_string(**kwargs) -> str:
        Returns a string representation of the portfolio review results.
    print(**kwargs) -> None:
        Prints the string representation of the portfolio review results.
    """

    portfolio_review: pd.DataFrame

    def to_df(self) -> pd.DataFrame:
        """
        Returns a copy of the portfolio review results as a pandas DataFrame.

        Returns
        -------
        pd.DataFrame
            a copy of the portfolio review results
        """

        return self.portfolio_review.copy()

    def to_string(self, **kwargs) -> str:
        """
        Returns a string representation of the portfolio review results.

        Parameters
        ----------
        **kwargs
            arbitrary keyword arguments

        Returns
        -------
        str
            a string representation of the portfolio review results
        """

        return self.portfolio_review.to_string(float_format="{:,.2f}%".format, **kwargs)

    def print(self, **kwargs) -> None:
        """
        Prints the string representation of the portfolio review results.

        Parameters
        ----------
        **kwargs
            arbitrary keyword arguments
        """

        print(self.to_string(**kwargs))
