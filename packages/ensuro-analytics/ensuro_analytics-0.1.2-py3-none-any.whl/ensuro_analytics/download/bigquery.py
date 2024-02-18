"""
Utils to download ensuro data
"""

import json
from typing import List, Optional

import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account

DEFAULT_POLICIES_TABLE_COLUMNS = [
    "id",
    "ensuro_id",
    "payout",
    "loss_prob",
    "jr_scr",
    "sr_scr",
    "pure_premium",
    "ensuro_commission",
    "partner_commission",
    "jr_coc",
    "sr_coc",
    "start",
    "expiration",
    "actual_payout",
    "expired_on",
    "premium",
    "active",
    "progress",
    "duration_expected",
    "duration_actual",
    "risk_module",
    "rm_name",
    "quote",
]

DATETIME_COLUMNS = ["date", "start", "expiration", "expired_on"]


class BigQueryInterface:
    """
    A class used to interact with the Google BigQuery API.

    Attributes
    ----------
    project_id : str
        the Google Cloud project ID
    dataset_name : str
        the name of the dataset in BigQuery
    account_key_path : Optional[str]
        the path to the service account key file
    policies_table_columns : Optional[list[str]]
        the list of columns to fetch from the policies table
    credentials : google.auth.credentials.Credentials
        the credentials to use for the BigQuery client
    Client : google.cloud.bigquery.client.Client
        the BigQuery client

    Methods
    -------
    _date_cols_to_datetime(df: pd.DataFrame, columns: List[str] = DATETIME_COLUMNS) -> pd.DataFrame:
        Converts the specified columns of the dataframe to datetime.
    _bytes_to_dict(col: pd.Series) -> pd.Series:
        Converts a series of bytes to a series of dictionaries.
    sql(sql_query: str) -> pd.DataFrame:
        Executes a SQL query and returns the result as a dataframe.
    policies_table(limit: Optional[int] = None) -> pd.DataFrame:
        Fetches data from the policies table and returns it as a dataframe.
    time_series_table() -> pd.DataFrame:
        Fetches data from the time series table and returns it as a dataframe.
    fetch_data(table: str) -> pd.DataFrame:
        Fetches data from the specified table and returns it as a dataframe.
    """

    def __init__(
        self,
        project_id: str,
        dataset_name: str,
        account_key_path: Optional[str] = None,
        policies_table_columns: Optional[list[str]] = None,
    ):
        """
        Constructs a new BigQueryInterface object.

        Parameters
        ----------
        project_id : str
            the Google Cloud project ID
        dataset_name : str
            the name of the dataset in BigQuery
        account_key_path : Optional[str]
            the path to the service account key file
        policies_table_columns : Optional[list[str]]
            the list of columns to fetch from the policies table
        """
        self.project_id = project_id
        self.dataset_name = dataset_name
        self.account_key_path = account_key_path
        self.credentials = None

        if self.account_key_path is not None:
            self.credentials = service_account.Credentials.from_service_account_file(self.account_key_path)

        self.Client = bigquery.Client(credentials=self.credentials, project=self.project_id)

        if policies_table_columns is None:
            self.policies_table_columns = DEFAULT_POLICIES_TABLE_COLUMNS
        else:
            self.policies_table_columns = policies_table_columns

    @staticmethod
    def _date_cols_to_datetime(df: pd.DataFrame, columns: List[str] = DATETIME_COLUMNS):
        """
        Converts the specified columns of the dataframe to datetime.

        Parameters
        ----------
        df : pd.DataFrame
            The dataframe whose columns are to be converted.
        columns : List[str], optional
            The list of column names to convert, by default DATETIME_COLUMNS

        Returns
        -------
        pd.DataFrame
            The dataframe with the specified columns converted to datetime.
        """
        for col in columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col])
        return df

    @staticmethod
    def _bytes_to_dict(col: pd.Series) -> pd.Series:
        """
        Converts a series of bytes to a series of dictionaries.

        Parameters
        ----------
        col : pd.Series
            The pandas Series containing bytes to be converted.

        Returns
        -------
        pd.Series
            The pandas Series where each byte has been converted to a dictionary.
        """
        quote_types = col.apply(type).unique()
        if bytes in quote_types:
            col = col.apply(lambda x: x.decode("utf-8") if isinstance(x, bytes) else x)
            col = col.apply(lambda x: json.loads(x) if isinstance(x, str) else x)
        return col

    def sql(self, sql_query: str) -> pd.DataFrame:
        """
        Executes a SQL query and returns the result as a dataframe.

        Parameters
        ----------
        sql_query : str
            The SQL query to be executed.

        Returns
        -------
        pd.DataFrame
            The result of the SQL query as a dataframe.
        """
        df = self.Client.query(sql_query).to_dataframe()
        return df

    def policies_table(self, limit: Optional[int] = None) -> pd.DataFrame:
        """
        Fetches data from the policies table and returns it as a dataframe.

        Parameters
        ----------
        limit : Optional[int]
            The maximum number of rows to return.

        Returns
        -------
        pd.DataFrame
            The data from the policies table as a dataframe.
        """
        columns_str = ", ".join(self.policies_table_columns)
        sql_query = f"SELECT * FROM `{self.project_id}.{self.dataset_name}.policies_table`"
        if limit is not None:
            sql_query += f" ORDER BY id DESC LIMIT {limit}"
        sql_query = f"SELECT {columns_str} FROM ({sql_query}) ORDER BY id ASC"

        data = self._date_cols_to_datetime(self.sql(sql_query))
        data["quote"] = self._bytes_to_dict(data.quote)

        return data

    def time_series_table(self) -> pd.DataFrame:
        """
        Fetches data from the time series table and returns it as a dataframe.

        Returns
        -------
        pd.DataFrame
            The data from the time series table as a dataframe.
        """
        sql_query = f"SELECT * FROM `{self.project_id}.{self.dataset_name}.time_series`"
        return self._date_cols_to_datetime(self.sql(sql_query))

    def fetch_data(self, table: str) -> pd.DataFrame:
        """
        Fetches data from the specified table and returns it as a dataframe.

        Parameters
        ----------
        table : str
            The name of the table to fetch data from. Must be either 'policies' or 'time-series'.

        Returns
        -------
        pd.DataFrame
            The data from the specified table as a dataframe.

        Raises
        ------
        AssertionError
            If the table name is not 'policies' or 'time-series'.
        """
        assert table in ["policies", "time-series"], "table must be either 'policies' or 'time-series'"

        if table == "policies":
            data = self.policies_table()
        elif table == "time-series":
            data = self.time_series_table()

        return data
