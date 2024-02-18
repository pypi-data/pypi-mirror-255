from abc import ABC, abstractmethod
from datetime import datetime
import pandas as pd
import numpy as np
from volstreet.config import logger
from volstreet.backtests.framework import BackTester, rearrange_options_prices
from volstreet.backtests.underlying_info import UnderlyingInfo
from volstreet.utils import find_strike


class IntradayBackTest(BackTester, ABC):
    def __init__(self, underlying: UnderlyingInfo):
        self.underlying = underlying
        self.expiry = None
        self._option_prices = pd.DataFrame()
        self.unique_strikes = []
        super().__init__()

    @property
    def option_prices(self):
        return self._option_prices

    @option_prices.setter
    def option_prices(self, new_prices):
        assert isinstance(new_prices, pd.DataFrame)
        if self.expiry is not None:
            assert new_prices.expiry.unique() == self.expiry.strftime("%d%b%y").upper()
        self._option_prices = (
            new_prices.reset_index()
            .drop_duplicates(subset=["timestamp", "strike", "expiry"])
            .set_index("timestamp")
        )
        self.unique_strikes = np.unique(
            self.unique_strikes + new_prices.strike.unique().tolist()
        ).tolist()

    def determine_expiry(self, initiation_info: pd.Series):
        nearest_expiry = self.fetch_nearest_expiry_from_date(
            self.underlying.name, initiation_info.name
        )
        return nearest_expiry

    def snapshot_at_entry(
        self, initiation_info: pd.Series, num_strikes: int
    ) -> pd.DataFrame:
        """Currently only supports straddle and not strangle"""
        initiation_info = initiation_info.to_frame().T
        snapshot = self._build_option_chain_skeleton(
            self.underlying.name, initiation_info, num_strikes, threshold_days_expiry=0
        )
        return snapshot

    def fetch_and_store_option_prices(
        self,
        initiation_info: pd.Series,
        num_strikes: int,
    ):
        """This function will take in the daily prices of the index
        Important: This function uses generate_query_for_option_prices method of Database class and not
        cte_entries_to_query method. This is because we need to fetch the option prices for the entire
        week."""

        atm_strike = find_strike(initiation_info.open, self.underlying.base)
        strike_range = np.arange(
            atm_strike - num_strikes * self.underlying.base,
            atm_strike + num_strikes * self.underlying.base + self.underlying.base,
            self.underlying.base,
        )
        query = self.generate_query_for_option_prices(
            self.underlying.name,
            [self.expiry.strftime("%d%b%y").upper()],
            [strike for strike in strike_range],
            from_date=initiation_info.name.strftime("%Y-%m-%d %H:%M"),
            to_date=self.expiry.strftime("%Y-%m-%d %H:%M"),
        )
        prices = self.fetch_option_prices(query)
        prices = rearrange_options_prices(prices).rename(
            columns={"CE": "call_price", "PE": "put_price"}
        )
        self.option_prices = pd.concat([self.option_prices, prices]).sort_index()

        return prices

    def fetch_missed_strikes(
        self,
        strikes: list[int | float],
        from_date: datetime,
    ):
        query = self.generate_query_for_option_prices(
            self.underlying.name,
            [self.expiry.strftime("%d%b%y").upper()],
            strikes,
            from_date=from_date.strftime("%Y-%m-%d %H:%M"),
            to_date=self.expiry.strftime("%Y-%m-%d %H:%M"),
        )
        prices = self.fetch_option_prices(query)
        prices = rearrange_options_prices(prices).rename(
            columns={"CE": "call_price", "PE": "put_price"}
        )
        self.option_prices = pd.concat([self.option_prices, prices]).sort_index()

    def strike_available(self, new_strikes: list[int | float]) -> list[bool]:
        return [strike in self.unique_strikes for strike in new_strikes]

    def check_option_prices_availability(
        self,
        date_frame_to_merge: pd.DataFrame,
    ) -> None:
        option_prices = self.option_prices.reset_index()
        date_frame_to_merge = date_frame_to_merge.reset_index()

        # Get the list of strike columns from the subclass
        strike_columns = self.get_strike_columns()

        # Create a set of unique combinations of timestamp and strikes from the option_prices DataFrame
        available_options = set(
            option_prices[["timestamp", "strike"]].apply(tuple, axis=1)
        )

        # Initialize a DataFrame to hold all missing strike information
        missing_strikes_info = pd.DataFrame()

        # Check for strike availability for each specified column
        for strike_col in strike_columns:
            missing_strikes = date_frame_to_merge[
                ~date_frame_to_merge[["timestamp", strike_col]]
                .apply(tuple, axis=1)
                .isin(available_options)
            ]

            # Add a column to specify the type of strike that is missing
            missing_strikes["missing_strike_type"] = strike_col

            # Append missing strikes to the info DataFrame
            missing_strikes_info = pd.concat(
                [missing_strikes_info, missing_strikes], ignore_index=True
            )

        # Report missing strikes
        if not missing_strikes_info.empty:
            logger.error(
                f"Missing option price data for the following combinations:\n{missing_strikes_info}"
            )

    @abstractmethod
    def get_strike_columns(self):
        pass
