"""
Utils to fetch data from Ensuro's API
"""
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import requests
import yaml

from . import get_from_quote

RISK_MODULES_API_ADDRESS = "https://offchain-v2.ensuro.co/api/riskmodules/"


class OffchainAPI:
    """
    Class for interacting with the offchain API.

    It provides low-level primitives (GET) for a single call, and high-level methods for combining multiple calls.
    """

    def __init__(self, url, page_size=1000, private_key=None):
        self.url = url.strip("/")
        self.page_size = page_size
        self.private_key = private_key
        self.session = requests.Session()
        if private_key:
            self.session.headers.update({"Authorization": f"Token {private_key}"})

    def __repr__(self):
        return f"<OffchainAPI url={self.url}>"

    def url_to_endpoint(self, url):
        """
        Returns the endpoint for the given URL. Useful for links returned by the API.
        """
        if url.startswith(self.url):
            url = url[len(self.url) :]
        return url.strip("/")

    def endpoint_url(self, endpoint):
        """
        Returns the full URL for the given endpoint.
        """
        if endpoint.startswith(self.url):
            endpoint = endpoint[len(self.url) :]
        return f"{self.url}/{endpoint.strip('/')}/"

    def get(self, endpoint, query_params: dict = None, validate_response=True):
        """
        Low level GET call to the given endpoint.
        """
        response = self.session.get(self.endpoint_url(endpoint), params=query_params)
        if validate_response:
            response.raise_for_status()
        return response

    def get_policies(self):
        """
        Returns a list with all the policies.
        """
        policies = []
        url = self.endpoint_url("policies") + f"?limit={self.page_size}"
        if self.private_key is not None:
            url += "&private_data=True"

        while url is not None:
            response = self.session.get(url)
            response.raise_for_status()
            policies += response.json()["results"]
            url = response.json()["next"]

        return policies

    @staticmethod
    def get_expiration_date(row, version="v2"):
        """
        Computes the actual expiration date for a policy
        :param row: row of the policy dataset as it comes from API
        :param version: dataset from API V1 or API V2
        :return: actual expiration date
        """
        if version == "v1":
            colname = "tx"
        elif version == "v2":
            colname = "event"
        else:
            raise ValueError

        transactions_list = row[f"{colname}s"]
        for transaction in transactions_list:
            if transaction[f"{colname}_type"] == "resolution":
                return transaction["timestamp"]
        return np.nan

    def build_policies_table(self, quote_columns: Optional[str | Path] = None):
        """
        Downloads data from Ensuro's API and transforms it in the "standard" Ensuro policies table.
        """
        # Get Policies Data
        policies = self.get_policies()
        # create dataset
        df = pd.DataFrame.from_records(policies).fillna(np.nan)
        to_numeric = [
            "payout",
            "premium",
            "jr_scr",
            "sr_scr",
            "loss_prob",
            "pure_premium",
            "ensuro_commission",
            "partner_commission",
            "jr_coc",
            "sr_coc",
            "actual_payout",
        ]
        df[to_numeric] = df[to_numeric].astype(float)

        # Transform data
        now = pd.to_datetime("today")

        expiration_dates = [self.get_expiration_date(row, version="v2") for row in policies]
        df["expired_on"] = expiration_dates
        df.loc[df.actual_payout == 0, "expired_on"] = df.loc[df.actual_payout == 0, "expiration"].values

        # format dates
        df["start"] = pd.to_datetime(df.start).dt.tz_localize(None)
        df["expiration"] = pd.to_datetime(df.expiration).dt.tz_localize(None)
        df["expired_on"] = pd.to_datetime(df.expired_on).dt.tz_localize(None)
        df["active"] = df.actual_payout.apply(np.isnan)

        df["progress"] = (now - df.start).apply(lambda x: np.timedelta64(x) / np.timedelta64(1, "s"))
        df["progress"] = df["progress"] / (df.expiration - df.start).apply(
            lambda x: np.timedelta64(x) / np.timedelta64(1, "s")
        )
        df.loc[~df.active, "progress"] = 1.0

        df["duration_expected"] = (df.expiration - df.start).apply(lambda x: x / np.timedelta64(1, "D"))
        df["duration_actual"] = (df.expired_on - df.start).apply(lambda x: x / np.timedelta64(1, "D"))

        # create risk module
        df["risk_module"] = df["rm"].apply(lambda x: x.split("/")[-2])

        df["partner"] = [get_from_quote(x, "partnerName") for x in df.quote]
        df["ttype"] = [get_from_quote(x, "ticketType") for x in df.quote]

        if quote_columns is not None:
            # Create columns out of quote
            with open(quote_columns, "r") as f:
                quote_columns_dict = yaml.safe_load(f)

            for key, columns in quote_columns_dict.items():
                for column in columns:
                    df[column] = [get_from_quote(x, column) for x in df.quote]

        df["start_date"] = pd.to_datetime(df.start).dt.date

        risk_modules = requests.get(RISK_MODULES_API_ADDRESS)
        risk_modules = risk_modules.json()
        risk_modules = dict(zip([x["address"] for x in risk_modules], [x["name"] for x in risk_modules]))

        df["rm_name"] = df.risk_module.map(risk_modules)

        df["start_date"] = pd.to_datetime(df["start_date"])
        df["date_price_applied"] = (
            df.groupby(["rm_name", "loss_prob"]).start.transform("min").apply(lambda x: str(x.date()))
        )

        return df
