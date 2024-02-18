from attrs import define, field
from collections import defaultdict
from sqlalchemy import create_engine, text, TextClause
from itertools import product
from datetime import datetime
import numpy as np
from typing import Optional, Iterable, List
import os
from volstreet import timeit
import pandas as pd


@define
class DataBaseConnection:
    # Database attributes
    mode: str = field(default="timescale", repr=False)
    _DB_NAME: str = field(default=None, repr=False)
    _DB_USER: str = field(default=None, repr=False)
    _DB_PASS: str = field(default=None, repr=False)
    _DB_HOST: str = field(default=None, repr=False)
    _DB_PORT: str = field(default=None, repr=False)
    _database_connection_url: str = field(default=None, repr=False)
    _alchemy_engine_url: str = field(default=None, repr=False)

    # Storing queries to see if caching is possible
    _queries: defaultdict = field(
        factory=lambda: defaultdict(list), init=False, repr=False
    )

    def __attrs_post_init__(self):
        if self._DB_USER is None:
            self._set_db_credentials()
        self._set_database_connection_urls()

    @staticmethod
    def _get_env_var(var_name: str):
        """Fetch environment variables safely."""
        var_value = os.getenv(var_name)
        if var_value is None:
            raise EnvironmentError(f"Environment variable '{var_name}' is not set.")
        return var_value

    def _set_db_credentials(self):
        if self.mode == "timescale":
            var_prefix = "TSDB"
        elif self.mode == "local":
            var_prefix = "LOCALDB"
        else:
            raise ValueError(f"Invalid mode '{self.mode}'")
        self._DB_NAME = self._get_env_var(f"{var_prefix}_DBNAME")
        self._DB_USER = self._get_env_var(f"{var_prefix}_USER")
        self._DB_PASS = self._get_env_var(f"{var_prefix}_PASS")
        self._DB_HOST = self._get_env_var(f"{var_prefix}_HOST")
        self._DB_PORT = self._get_env_var(f"{var_prefix}_PORT")

    def _set_database_connection_urls(self):
        self._database_connection_url = (
            f"postgres://{self._DB_USER}:{self._DB_PASS}@{self._DB_HOST}:"
            f"{self._DB_PORT}/{self._DB_NAME}"
        )
        self._database_connection_url += (
            "?sslmode=require" if self.mode == "timescale" else ""
        )
        self._alchemy_engine_url = "postgresql" + self._database_connection_url[8:]

    @property
    def executed_queries(self):
        return self._queries

    @staticmethod
    def generate_query_for_option_prices_df(
        index: str,
        df: pd.DataFrame,
        option_type: Optional[str] = None,
        cols_to_return: Optional[Iterable[str]] = None,
    ) -> text:
        if cols_to_return is None:
            cols_to_return = ["timestamp", "expiry", "strike", "option_type", "close"]

        columns_str = ", ".join([f"index_options.{x}" for x in cols_to_return])

        # Check if 'strike' contains tuples or floats
        first_strike = df.iloc[0]["strikes"]
        if isinstance(first_strike, (tuple, list)):
            cte_entries = [
                f"('{row.timestamp}'::timestamp, {strikes[0]}::integer, '{row.expiry}'::text, 'CE'::text), "
                f"('{row.timestamp}'::timestamp, {strikes[1]}::integer, '{row.expiry}'::text, 'PE'::text)"
                for row in df.itertuples(index=False)
                for strikes in [row.strikes]
            ]
        else:
            if option_type is None:
                raise ValueError(
                    "Option type must be provided if single strikes are provided."
                )

            # Add option_type column if it doesn't exist
            df["option_type"] = option_type

            cte_entries = [
                f"('{row.timestamp}'::timestamp, {row.strikes}::integer, '{row.expiry}'::text, '{row.option_type}'::text)"
                for row in df.itertuples(index=False)
            ]

        cte_entries_str = ", ".join(cte_entries)
        cte = f"WITH conditions AS (SELECT * FROM (VALUES {cte_entries_str}) AS t(timestamp, strike, expiry, option_type))"

        sql_query = text(
            f"""
            {cte}
            SELECT {columns_str}
            FROM index_options
            INNER JOIN conditions
            ON index_options.timestamp = conditions.timestamp 
               AND index_options.expiry = conditions.expiry
               AND index_options.strike = conditions.strike
               AND index_options.option_type = conditions.option_type
            WHERE index_options.underlying = '{index}';
            """
        )

        return sql_query

    @staticmethod
    def generate_query_for_option_prices(
        index: str,
        expirys: List[str],
        strikes: List[float | int],
        timestamps: Optional[List[str]] = None,
        from_date: Optional[datetime | str] = None,
        to_date: Optional[datetime | str] = None,
        option_type: Optional[str] = None,
        cols_to_return: Optional[Iterable[str]] = None,
    ) -> TextClause:
        if cols_to_return is None:
            cols_to_return = [
                "timestamp",
                "expiry",
                "strike",
                "option_type",
                "close",
            ]

        columns_str = ", ".join([f"index_options.{x}" for x in cols_to_return])

        # Convert strikes to int if they are float
        strikes = [
            int(strike) if isinstance(strike, float) else strike for strike in strikes
        ]
        strikes = list(np.unique(strikes))
        expirys = list(np.unique(expirys))

        timestamp_condition = ""
        if from_date and to_date:
            timestamp_condition = f"AND index_options.timestamp >= '{from_date}' AND index_options.timestamp <= '{to_date}'"
        elif timestamps:
            timestamps = list(np.unique(timestamps))
            timestamp_condition = f"AND index_options.timestamp IN ({', '.join([f'{repr(ts)}' for ts in timestamps])})"

        all_combinations = list(product(expirys, strikes))

        cte_entries_list = []
        for expiry, strike in all_combinations:
            if option_type:
                cte_entries_list.append(
                    (
                        strike,
                        expiry,
                        f"'{option_type}'::text",
                    )
                )
            else:
                cte_entries_list.extend(
                    [
                        (strike, expiry, "'CE'::text"),
                        (strike, expiry, "'PE'::text"),
                    ]
                )

        # Sort the conditions by strike
        cte_entries_list.sort(key=lambda x: x[0])
        cte_entries = ", ".join(
            [
                f"({strike}::integer, '{expiry}'::text, {option_type})"
                for strike, expiry, option_type in cte_entries_list
            ]
        )
        cte = f"WITH conditions AS (SELECT * FROM (VALUES {cte_entries}) AS t(strike, expiry, option_type))"

        sql_query = text(
            f"""
            {cte}
            SELECT {columns_str}
            FROM index_options
            INNER JOIN conditions
            ON index_options.expiry = conditions.expiry
               AND index_options.strike = conditions.strike
               AND index_options.option_type = conditions.option_type
            WHERE index_options.underlying = '{index}'
            {timestamp_condition};
        """
        )

        return sql_query

    @timeit()
    def fetch_historical_expiries(self, underlying_name: str) -> list[str]:
        """Fetch historical expiries for the given underlying."""
        query = text(
            f"""
            SELECT DISTINCT expiry
            FROM index_options
            WHERE underlying = '{underlying_name}';
            """
        )

        engine = create_engine(self._alchemy_engine_url)
        with engine.connect() as connection:
            expiries = pd.read_sql(query, connection)

        return expiries["expiry"].tolist()

    @timeit()
    def fetch_option_prices(self, query: str | TextClause) -> pd.DataFrame:
        """Fetch option prices from TimescaleDB using the provided query."""

        engine = create_engine(self._alchemy_engine_url)
        with engine.connect() as connection:
            option_prices = pd.read_sql(query, connection)

        # Store the query
        self._queries["index_options"].append(query)
        return option_prices

    @timeit()
    def fetch_index_prices(
        self,
        underlying: str,
        from_timestamp: str | pd.Timestamp | datetime | None = None,
        to_timestamp: str | pd.Timestamp | datetime | None = None,
    ) -> pd.DataFrame:
        """Fetch index prices from TimescaleDB."""
        query = f"""
            SELECT *
            FROM index_prices
            WHERE underlying = '{underlying}'
        """

        if from_timestamp:
            query += f"AND timestamp >= '{from_timestamp}'"

        if to_timestamp:
            if isinstance(to_timestamp, str) and " " not in to_timestamp:
                to_timestamp += (
                    " 15:30"  # Add 15:30 to the date if only date is provided
                )
            query += f"AND timestamp <= '{to_timestamp}'"

        # Add order by clause to sort by timestamp
        query += " ORDER BY timestamp ASC;"

        query = text(query)

        engine = create_engine(self._alchemy_engine_url)
        with engine.connect() as connection:
            index_prices = pd.read_sql(query, connection)

        # Store the query
        self._queries["index_prices"].append(query)

        return index_prices

    def execute_query(self, query: str | TextClause, return_type: str = "fetchall"):
        """Execute the provided query."""
        query = text(query) if isinstance(query, str) else query
        engine = create_engine(self._alchemy_engine_url)
        with engine.connect() as connection:
            result = connection.execute(query)
            result = getattr(result, return_type)()

        return result
