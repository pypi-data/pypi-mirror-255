import pandas as pd
import numpy as np
from enum import Enum
from sqlalchemy import text
from datetime import datetime, timedelta, time
from attrs import define, field
from volstreet.datamodule.eod_client import EODClient
from volstreet.utils import find_strike
from volstreet.blackscholes import call, put, calculate_strangle_iv
from volstreet.backtests.database import DataBaseConnection
from volstreet.backtests.underlying_info import UnderlyingInfo
from volstreet.backtests.tools import (
    nav_drawdown_analyser,
    prepare_index_prices_for_backtest,
)


class Signal(Enum):
    BUY = 1
    SELL = -1


@define
class BackTester(DataBaseConnection):
    eod_client: EODClient = field(factory=EODClient, repr=False)
    index_instances: dict = field(factory=dict, init=False, repr=False)

    def __attrs_post_init__(self):
        self._initialize_index_instances()
        super().__attrs_post_init__()

    def _initialize_index_instances(self):
        self.index_instances.update(
            {
                "NIFTY": UnderlyingInfo("NIFTY"),
                "BANKNIFTY": UnderlyingInfo("BANKNIFTY"),
                "FINNIFTY": UnderlyingInfo("FINNIFTY"),
                "MIDCPNIFTY": UnderlyingInfo("MIDCPNIFTY"),
            }
        )

    def fetch_nearest_expiry_from_date(
        self,
        index: str,
        date_time: str | datetime,
        threshold_days: int = 0,
        n_exp: int = 1,
    ) -> pd.DatetimeIndex | pd.Timestamp | None:
        if isinstance(date_time, str):
            date_time = pd.to_datetime(date_time)

        filtered_dates = self.index_instances[index].expiry_dates
        delta_days = (filtered_dates - date_time.replace(hour=00, minute=00)).days
        valid_indices = np.where(
            delta_days < threshold_days, np.inf, delta_days
        ).argsort()[:n_exp]

        nearest_exp_dates = filtered_dates[valid_indices].sort_values()

        if n_exp == 1:
            return nearest_exp_dates[0] if len(nearest_exp_dates) != 0 else None
        else:
            return nearest_exp_dates

    def historic_time_to_expiry(
        self,
        index: str,
        date_time: str | datetime,
        in_days: bool = False,
        threshold_days: int = 0,
        n_exp: int = 1,
    ) -> float | np.ndarray | None:
        """Return time left to expiry"""
        if in_days:
            multiplier = 365
            rounding = 0
        else:
            multiplier = 1
            rounding = 5

        if isinstance(date_time, str):
            date_time = pd.to_datetime(date_time)

        expiry = self.fetch_nearest_expiry_from_date(
            index=index,
            date_time=date_time.replace(hour=00, minute=00),
            threshold_days=threshold_days,
            n_exp=n_exp,
        )

        if expiry is None:
            return None
        else:
            time_left = (expiry - date_time) / timedelta(days=365)

        # Multiplying by the multiplier and rounding
        time_left = np.round(time_left * multiplier, rounding)
        return time_left

    @staticmethod
    def _melt_skeleton(df: pd.DataFrame) -> pd.DataFrame:
        # Step 1: Create a new DataFrame with square-up information if it exists

        if "square_up_timestamp" not in df.columns:
            concat_df = df[["timestamp", "expiry", "call_strike", "put_strike"]].copy()
        else:
            square_up_df = df[
                [
                    "square_up_timestamp",
                    "square_up_expiry",
                    "square_up_call_strike",
                    "square_up_put_strike",
                ]
            ].copy()

            # Step 2: Rename columns to match the original DataFrame
            square_up_df.rename(
                columns={
                    "square_up_timestamp": "timestamp",
                    "square_up_expiry": "expiry",
                    "square_up_call_strike": "call_strike",
                    "square_up_put_strike": "put_strike",
                },
                inplace=True,
            )

            # Concatenate the DataFrames
            concat_df = pd.concat([df, square_up_df])

        # Remove rows where any key columns are NaN
        concat_df.dropna(
            subset=["timestamp", "expiry", "call_strike", "put_strike"], inplace=True
        )

        # Step 4: Combine 'call_strike' and 'put_strike' into a single tuple column
        concat_df["strikes"] = list(
            zip(concat_df["call_strike"], concat_df["put_strike"])
        )

        # Drop the individual 'call_strike' and 'put_strike' columns as they are now redundant
        concat_df.drop(["call_strike", "put_strike"], axis=1, inplace=True)

        # Sort the DataFrame by timestamp for better readability and analysis
        concat_df.sort_values(by=["timestamp"], inplace=True)

        # Reset the index after sorting
        concat_df.reset_index(drop=True, inplace=True)

        return concat_df[["timestamp", "expiry", "strikes"]]

    def _fetch_option_prices_from_skeleton(
        self,
        skeleton: pd.DataFrame,
        index: str,
    ) -> pd.DataFrame:
        df = self._melt_skeleton(skeleton)

        query = self.generate_query_for_option_prices_df(
            index=index,
            df=df,
        )

        option_prices = self.fetch_option_prices(query)

        option_prices = (
            option_prices.groupby(["timestamp", "expiry", "strike", "option_type"])
            .close.first()
            .unstack(level="option_type")
            .reset_index()
        )

        return option_prices

    def _build_option_chain_skeleton(
        self,
        underlying: str,
        df: pd.DataFrame,
        num_strikes: int = 3,
        num_exp: int = 1,
        threshold_days_expiry: int | float = 1,
    ) -> pd.DataFrame:
        """Supply a dataframe with a datetime index and a open column."""

        df = df.copy()
        df.index.name = "timestamp"

        # Finding ATM strike and renaming the columns
        df = df.reset_index()
        df["atm_strike"] = df.open.apply(
            lambda x: find_strike(x, self.index_instances[underlying].base)
        )

        # Adding expiry
        df["expiry"] = df.timestamp.apply(
            lambda x: self.fetch_nearest_expiry_from_date(
                index=underlying,
                date_time=x,
                threshold_days=threshold_days_expiry,
                n_exp=num_exp,
            ).strftime("%d%b%y")
        )

        df["time_to_expiry"] = df.apply(
            lambda row: self.historic_time_to_expiry(
                index=underlying,
                date_time=row.timestamp,
                threshold_days=threshold_days_expiry,
                n_exp=num_exp,
            ),
            axis=1,
        )

        max_offset = (num_strikes - 1) // 2
        strike_offsets = [
            self.index_instances[underlying].base * i
            for i in range(-max_offset, max_offset + 1)
        ]

        # Exploding the dataframe to include a list of closest strikes
        df["strike"] = df["atm_strike"].apply(
            lambda x: [x + offset for offset in strike_offsets]
        )

        df_exploded = df.explode("strike", ignore_index=True).explode(
            ["expiry", "time_to_expiry"], ignore_index=True
        )

        df_exploded["expiry"] = df_exploded.expiry.apply(lambda x: x.upper())

        df_exploded["call_strike"] = df_exploded.strike

        df_exploded["put_strike"] = df_exploded.strike

        return df_exploded

    def build_option_chain(
        self,
        index: str,
        df: pd.DataFrame,
        num_strikes: int = 3,
        num_exp: int = 1,
        threshold_days_expiry: int | float = 1,
    ) -> pd.DataFrame:
        """Builds an option chain at a certain minute on a certain day."""

        skeleton = self._build_option_chain_skeleton(
            index, df, num_strikes, num_exp, threshold_days_expiry
        )
        option_prices = self._fetch_option_prices_from_skeleton(skeleton, index)

        # Merging the two dataframes on the closest strikes and nearest expiry
        merged = pd.merge(
            option_prices,
            skeleton[
                [
                    "timestamp",
                    "open",
                    "atm_strike",
                    "strike",
                    "expiry",
                    "time_to_expiry",
                ]
            ],
            left_on=["timestamp", "strike", "expiry"],
            right_on=["timestamp", "strike", "expiry"],
        )

        return merged

    def build_trade_df(
        self,
        underlying: UnderlyingInfo,
        trade_entry_time: tuple[int, int],
        square_up_time_delta: timedelta,
        threshold_days_expiry: int
        | float = 1.1,  # On purpose because last timestamp in the database is 15:29
        strike_offset: float = 0,
        call_strike_offset: float | None = None,
        put_strike_offset: float | None = None,
        from_date: str | datetime = "2019-04-01",
        to_date: str | datetime = None,
    ):
        """This function is intended to replace the overnight and quick straddle skeleton"""

        underlying_prices = self.fetch_index_prices(
            underlying.name, from_timestamp=from_date, to_timestamp=to_date
        )
        underlying_prices.set_index("timestamp", inplace=True)
        trade_entry_time = time(*trade_entry_time)
        underlying_prices = underlying_prices.between_time(
            trade_entry_time, trade_entry_time
        )
        if square_up_time_delta > timedelta(days=1):  # todo: simplify this
            if square_up_time_delta != timedelta(days=7):
                raise ValueError(
                    "When square_up_time_delta is greater than 1 day, it must be 7 days."
                )
            underlying_prices = underlying_prices.loc[
                [
                    _date in underlying.expiry_dates.date
                    for _date in underlying_prices.index.date
                ]
            ]  # Expiry to expiry

        # Crucial step
        underlying_prices["trade_id"] = range(len(underlying_prices))

        df = add_strikes(
            underlying,
            underlying_prices,
            strike_offset,
            call_strike_offset,
            put_strike_offset,
        )

        df.reset_index(inplace=True)

        # Add expiry
        df["expiry"] = df.timestamp.apply(
            lambda x: self.fetch_nearest_expiry_from_date(
                index=underlying.name,
                date_time=x,
                threshold_days=threshold_days_expiry,
                n_exp=1,
            ).strftime("%d%b%y")
        ).str.upper()

        # Add time to expiry
        df["time_to_expiry"] = df.apply(
            lambda row: self.historic_time_to_expiry(
                index=underlying.name,
                date_time=row.timestamp,
                threshold_days=threshold_days_expiry,
                n_exp=1,
            ),
            axis=1,
        )

        # Square up info

        # Square up timestamp
        if square_up_time_delta >= timedelta(days=1):
            df["square_up_timestamp"] = df.timestamp.shift(-1)

        else:
            df["square_up_timestamp"] = df.timestamp + square_up_time_delta

        # Square up columns
        df["square_up_expiry"] = df.expiry
        df["square_up_call_strike"] = df.call_strike
        df["square_up_put_strike"] = df.put_strike

        # Square up time to expiry
        df["square_up_time_to_expiry"] = df.apply(
            lambda row: self.historic_time_to_expiry(
                index=underlying.name,
                date_time=row.square_up_timestamp,
                threshold_days=threshold_days_expiry - square_up_time_delta.days,
                n_exp=1,
            ),
            axis=1,
        )
        df = df.dropna()
        return df

    def backtest_trades(
        self, underlying: UnderlyingInfo, action: Signal, *args, **kwargs
    ):
        """This function is intended to replace the overnight and quick straddle backtest
        For details on the arguments, see the build_trade_df function"""
        trades = self.build_trade_df(underlying, *args, **kwargs)

        trades.drop(columns=["high", "low", "close"], inplace=True)

        # Generate CTE entries and convert to query
        cte_entries = generate_cte_entries_from_df(trades)
        query = convert_cte_entries_to_query(cte_entries, underlying.name)

        # Fetch, rearrange, and rename option prices
        option_prices = self.fetch_option_prices(query)
        option_prices = rearrange_options_prices(option_prices).reset_index()
        option_prices.rename(
            columns={"CE": "call_price", "PE": "put_price"}, inplace=True
        )

        # Populate trades with prices
        trades_with_prices = populate_with_option_prices(
            trades, option_prices, has_square_up=True
        )

        trades = trades_with_prices.merge(
            trades[
                [
                    "trade_id",
                    "underlying",
                    "open",
                    "time_to_expiry",
                    "square_up_time_to_expiry",
                ]
            ],
            on="trade_id",
        )

        # Calculating the pct change in price
        trades["pct_change"] = trades.open.pct_change()

        # Calculating the initial and square up premiums
        trades["entry_premium"] = trades.call_price + trades.put_price
        trades["square_up_premium"] = (
            trades.square_up_call_price + trades.square_up_put_price
        )

        # Calculating profit
        trades["profit"] = (
            trades.square_up_premium - trades.entry_premium
        ) * action.value

        # Calculating the profit percentage
        trades["profit_percentage"] = trades.profit / trades.open

        trades = trades.dropna()

        trades.set_index("square_up_timestamp", inplace=True)

        trades.index = pd.to_datetime(trades.index).date

        trades = nav_drawdown_analyser(
            trades, column_to_convert="profit_percentage", profit_in_pct=True
        )

        priority = [
            "open",
            "pct_change",
            "profit",
            "profit_percentage",
            "rolling_cagr",
            "drawdown",
        ]

        trades = trades[
            priority + [col for col in trades.columns if col not in priority]
        ]

        return trades

    def _build_overnight_backtest_skeleton(
        self,
        underlying: str,
        df: pd.DataFrame,
        iv_df: pd.DataFrame,
        threshold_days_expiry: int | float = 1,
        strike_offset: float = 0,
        call_strike_offset: float | None = None,
        put_strike_offset: float | None = None,
    ) -> pd.DataFrame:
        # DEPRECATE THIS FUNCTION
        """Returns the strikes and expiries for the overnight backtest.
        By default, the time for every-day is assumed to be 15:29."""

        number_of_seconds_in_a_year = 60 * 60 * 24 * 365

        df = df.copy()
        df.index.name = "timestamp"

        # Creating timestamp column
        df = df.reset_index()
        df["timestamp"] = df.timestamp.apply(lambda x: x + timedelta(minutes=929))

        # Adding the iv column
        iv_df.index = pd.to_datetime(
            iv_df.index
        ).date  # Making sure the index is datetime
        df["iv"] = df.apply(
            lambda row: iv_df.loc[row.timestamp.date(), "iv"]
            if row.timestamp.date() in iv_df.index
            else np.nan,
            axis=1,
        )

        # Setting the strikes
        if call_strike_offset is None:
            call_strike_offset = strike_offset

        if put_strike_offset is None:
            put_strike_offset = strike_offset

        df["call_strike"] = df.open.apply(
            lambda x: find_strike(
                x * (1 + call_strike_offset), self.index_instances[underlying].base
            )
        )
        df["put_strike"] = df.open.apply(
            lambda x: find_strike(
                x * (1 - put_strike_offset), self.index_instances[underlying].base
            )
        )

        # Adding expiry
        df["expiry"] = df.timestamp.apply(
            lambda x: self.fetch_nearest_expiry_from_date(
                index=underlying,
                date_time=x,
                threshold_days=threshold_days_expiry,
                n_exp=1,
            )
            .strftime("%d%b%y")
            .upper()
        )

        # Adding time to expiry
        df["time_to_expiry"] = df.apply(
            lambda row: self.historic_time_to_expiry(
                index=underlying,
                date_time=row.timestamp,
                threshold_days=threshold_days_expiry,
                n_exp=1,
            ),
            axis=1,
        )

        # Square up columns

        # Square up timestamp
        df["square_up_timestamp"] = df.timestamp

        # Square up strikes
        df["square_up_call_strike"] = df.call_strike.shift(1)
        df["square_up_put_strike"] = df.put_strike.shift(1)

        # Square up expiry
        df["square_up_expiry"] = df.expiry.shift(1)

        # The square-up time to expiry will be the timedelta between the current timestamp
        # and the next timestamp subtracted from the time to expiry
        df["square_up_time_to_expiry"] = (
            df.time_to_expiry
            - df.timestamp.diff().shift(-1).dt.total_seconds()
            / number_of_seconds_in_a_year
        ).shift(1)

        return df

    def _build_quick_straddle_skeleton(
        self,
        underlying: str,
        df: pd.DataFrame,
        iv_df: pd.DataFrame,
        num_strikes: int = 3,
        threshold_days_expiry: int | float = 0,
        strike_offset: float = 0,
        call_strike_offset: float | None = None,
        put_strike_offset: float | None = None,
        square_up_timedelta: timedelta = None,
    ) -> pd.DataFrame:
        # DEPRECATE THIS FUNCTION
        number_of_seconds_in_a_year = 60 * 60 * 24 * 365
        df = df.copy().reset_index()
        df.index.name = "timestamp"

        # Setting the strikes
        if call_strike_offset is None:
            call_strike_offset = strike_offset
        if put_strike_offset is None:
            put_strike_offset = strike_offset

        df["call_strike"] = df.open.apply(
            lambda x: find_strike(
                x * (1 + call_strike_offset), self.index_instances[underlying].base
            )
        )
        df["put_strike"] = df.open.apply(
            lambda x: find_strike(
                x * (1 - put_strike_offset), self.index_instances[underlying].base
            )
        )

        # Calculate surrounding strikes for call and put based on the number of strikes
        max_offset = (num_strikes - 1) // 2
        strike_offsets = [
            self.index_instances[underlying].base * i
            for i in range(-max_offset, max_offset + 1)
        ]
        df["call_strike"] = df.call_strike.apply(
            lambda x: [x + offset for offset in strike_offsets]
        )
        df["put_strike"] = df.put_strike.apply(
            lambda x: [x + offset for offset in strike_offsets]
        )

        # Exploding the DataFrame to have one row for each strike
        df = df.explode(["call_strike", "put_strike"])

        # Expiry and Time to Expiry
        df["expiry"] = df.timestamp.apply(
            lambda x: self.fetch_nearest_expiry_from_date(
                index=underlying,
                date_time=x,
                threshold_days=threshold_days_expiry,
                n_exp=1,
            ).strftime("%d%b%y")
        ).str.upper()

        df["time_to_expiry"] = df.apply(
            lambda row: self.historic_time_to_expiry(
                index=underlying,
                date_time=row.timestamp,
                threshold_days=threshold_days_expiry,
                n_exp=1,
            ),
            axis=1,
        )

        # Adding IV
        iv_df.index = pd.to_datetime(iv_df.index).date  # Ensure index is datetime
        df["iv"] = df.apply(
            lambda row: iv_df.loc[row.timestamp.date(), "iv"]
            if row.timestamp.date() in iv_df.index
            else np.nan,
            axis=1,
        )

        # Square-up columns
        if square_up_timedelta is not None:
            df["square_up_timestamp"] = df.timestamp + square_up_timedelta
            df["square_up_time_to_expiry"] = (
                df.time_to_expiry
                - square_up_timedelta.total_seconds() / number_of_seconds_in_a_year
            ).shift(1)

        return df

    def backtest_overnight_strategy(
        self,
        index: str,
        df: pd.DataFrame,
        iv_df: pd.DataFrame,
        threshold_days_expiry: int | float = 1,
        strike_offset: float = 0,
        call_strike_offset: float | None = None,
        put_strike_offset: float | None = None,
        invert_profit: bool = False,
        drop_missing: bool = True,
    ) -> pd.DataFrame:
        # DEPRECATE THIS FUNCTION
        """Supply a dataframe with a datetime index and a open column alongside other
        columns you want to include. The periodicity of the index will be considered as the duration
        of holding the position (this will decide the square-up time to expiry)."""

        skeleton = self._build_overnight_backtest_skeleton(
            index,
            df,
            iv_df,
            threshold_days_expiry,
            strike_offset,
            call_strike_offset,
            put_strike_offset,
        )
        option_prices = self._fetch_option_prices_from_skeleton(skeleton, index)

        call_prices = option_prices[["timestamp", "expiry", "strike", "CE"]]
        put_prices = option_prices[["timestamp", "expiry", "strike", "PE"]]

        # Merging for initiation option prices

        # Merging initial call prices
        merged = skeleton.merge(
            call_prices.rename(columns={"strike": "call_strike"}),
            on=["timestamp", "call_strike", "expiry"],
            how="left",
        ).rename(columns={"CE": "call_price_init"})

        # Merging initial put prices
        merged = merged.merge(
            put_prices.rename(columns={"strike": "put_strike"}),
            on=["timestamp", "put_strike", "expiry"],
            how="left",
        ).rename(columns={"PE": "put_price_init"})

        # Merging for square up option prices

        # Merging square up call prices
        merged = merged.merge(
            call_prices.rename(
                columns={
                    "expiry": "square_up_expiry",
                    "strike": "square_up_call_strike",
                }
            ),
            on=["timestamp", "square_up_call_strike", "square_up_expiry"],
            how="left",
        ).rename(columns={"CE": "call_price_square_up"})

        # Merging square up put prices
        merged = merged.merge(
            put_prices.rename(
                columns={"expiry": "square_up_expiry", "strike": "square_up_put_strike"}
            ),
            on=["timestamp", "square_up_put_strike", "square_up_expiry"],
            how="left",
        ).rename(columns={"PE": "put_price_square_up"})

        # Filling missing option prices while initiating the position
        filled: pd.DataFrame = self._fill_missing_option_prices(
            merged,
            col_names={
                "spot": "open",
                "call_strike": "call_strike",
                "put_strike": "put_strike",
                "time_to_expiry": "time_to_expiry",
                "iv": "iv",
                "call_price": "call_price_init",
                "put_price": "put_price_init",
            },
        )

        if drop_missing:
            # Drop rows where either initial call or put price is missing combined with missing iv
            condition = (
                filled["call_price_init"].isna() | filled["put_price_init"].isna()
            ) & (filled["iv"].isna())
            filled = filled[~condition]

        # Filling missing option prices while squaring up the position
        filled: pd.DataFrame = self._fill_missing_option_prices(
            filled,
            col_names={
                "spot": "open",
                "call_strike": "square_up_call_strike",
                "put_strike": "square_up_put_strike",
                "time_to_expiry": "square_up_time_to_expiry",
                "iv": "iv",
                "call_price": "call_price_square_up",
                "put_price": "put_price_square_up",
            },
        )

        if drop_missing:
            # Drop rows where either square up call or put price is missing combined with missing iv
            condition = (
                filled["call_price_square_up"].isna()
                | filled["put_price_square_up"].isna()
            ) & (filled["iv"].isna())
            filled = filled[~condition]

        # Calculating the initial and square up premiums
        filled["init_premium"] = filled.call_price_init + filled.put_price_init
        filled["square_up_premium"] = (
            filled.call_price_square_up + filled.put_price_square_up
        )

        # Setting initial premium to nan if square up cannot be identified for the position
        filled["init_premium"] = np.where(
            filled.expiry == (filled.square_up_expiry.shift(-1)),
            filled.init_premium,
            np.nan,
        )

        # Shifting the init_premium to the next period for profit calculation
        filled["init_premium"] = filled.init_premium.shift(1)

        # Calculating profit
        filled["profit"] = filled.init_premium - filled.square_up_premium

        if invert_profit:
            filled["profit"] = -filled["profit"]

        # Calculating the profit percentage
        filled["profit_percentage"] = filled.profit / filled.open.shift(1)

        return filled

    def backtest_quick_straddle(
        self,
        index: str,
        df: pd.DataFrame,
        iv_df: pd.DataFrame,
        num_strikes: int = 3,
        strike_offset: float = 0,
        call_strike_offset: float | None = None,
        put_strike_offset: float | None = None,
        square_up_timedelta: timedelta = 10,
    ) -> pd.DataFrame:
        # DEPRECATE THIS FUNCTION
        skeleton = self._build_quick_straddle_skeleton(
            index,
            df,
            iv_df,
            num_strikes,
            0,
            strike_offset,
            call_strike_offset,
            put_strike_offset,
            square_up_timedelta,
        )
        skeleton.reset_index(inplace=True, drop=True)
        option_prices = self._fetch_option_prices_from_skeleton(skeleton, index)

        call_prices = option_prices[["timestamp", "expiry", "strike", "CE"]]
        put_prices = option_prices[["timestamp", "expiry", "strike", "PE"]]

        # Merging initial call prices
        merged = skeleton.merge(
            call_prices.rename(columns={"strike": "call_strike"}),
            on=["timestamp", "call_strike", "expiry"],
            how="left",
        ).rename(columns={"CE": "call_price_init"})

        # Merging initial put prices
        merged = merged.merge(
            put_prices.rename(columns={"strike": "put_strike"}),
            on=["timestamp", "put_strike", "expiry"],
            how="left",
        ).rename(columns={"PE": "put_price_init"})
        # Merging square up call prices
        merged = merged.merge(
            call_prices.rename(
                columns={"strike": "call_strike", "timestamp": "square_up_timestamp"}
            ),
            on=["square_up_timestamp", "call_strike", "expiry"],
            how="left",
        ).rename(columns={"CE": "call_price_square_up"})

        # Merging square up put prices
        merged = merged.merge(
            put_prices.rename(
                columns={"strike": "put_strike", "timestamp": "square_up_timestamp"}
            ),
            on=["square_up_timestamp", "put_strike", "expiry"],
            how="left",
        ).rename(columns={"PE": "put_price_square_up"})

        return merged

    @staticmethod
    def prepare_option_chain_for_vol_surface(data_frame: pd.DataFrame) -> pd.DataFrame:
        def find_atm_iv(group):
            avg_iv = group[(group.strike == group.atm_strike)].avg_iv.values
            return avg_iv[0] if len(avg_iv) > 0 else np.nan

        data_frame = data_frame.dropna().copy()
        data_frame.rename(
            columns={"open": "spot", "CE": "call_price", "PE": "put_price"},
            inplace=True,
        )

        # Removing entries where the option price is less than the intrinsic value
        intrinsic_value = abs(data_frame["strike"] - data_frame["spot"])
        valid_entries = np.where(
            data_frame["spot"] > data_frame["strike"],
            data_frame["call_price"] > intrinsic_value,
            data_frame["put_price"] > intrinsic_value,
        )
        data_frame = data_frame[valid_entries]

        # Adding ivs
        data_frame[["call_iv", "put_iv", "avg_iv"]] = (
            data_frame.apply(
                lambda row: calculate_strangle_iv(
                    row.call_price,
                    row.put_price,
                    row.spot,
                    strike=row.strike,
                    time_left=row.time_to_expiry,
                ),
                axis=1,
            )
            .apply(pd.Series)
            .values
        )

        # Adding atm_iv for the timestamp
        atm_iv_for_timestamp = data_frame.groupby(["timestamp", "expiry"]).apply(
            find_atm_iv
        )
        timestamp_expiry_pairs = pd.MultiIndex.from_arrays(
            [data_frame.timestamp, data_frame.expiry]
        )
        data_frame["atm_iv"] = atm_iv_for_timestamp.loc[timestamp_expiry_pairs].values

        # Adding the distance feature
        data_frame["distance"] = data_frame["strike"] / data_frame["spot"] - 1

        # Adding the iv multiple feature
        data_frame["iv_multiple"] = data_frame["avg_iv"] / data_frame["atm_iv"]

        # Adding the distance squared feature
        data_frame["distance_squared"] = data_frame["distance"] ** 2

        # Adding the money-ness feature (ratio of spot price to strike price)
        data_frame["money_ness"] = data_frame["spot"] / data_frame["strike"]

        # Adding the interaction term between distance squared and time to expiry
        data_frame["distance_time_interaction"] = (
            data_frame["distance_squared"] * data_frame["time_to_expiry"]
        )

        return data_frame

    @staticmethod
    def backtest_trades_wip(
        group: pd.DataFrame,
        trigger_timestamps: pd.Series,
        action: int,
        target_pct: float | None = None,
        sl_pct: float = 0.003,
    ):
        """The group is a dataframe of the OHLC data for a single day."""

        # Filter trigger timestamps to the same date as the group
        trigger_timestamps = trigger_timestamps[
            trigger_timestamps.index.date == group.index[0].date()
        ]

        all_entries_in_group = []

        for trigger_time in trigger_timestamps.index:
            trade_info_dict = {"trigger_time": trigger_time}
            try:
                entry_price = group.loc[trigger_time, "close"]
            except KeyError:
                # If the trigger time is not in the group, skip it
                continue

            # Setting SL and TP prices
            sl_price = entry_price * (1 - sl_pct * action)
            target_price = (
                entry_price * (1 + target_pct * action)
                if target_pct
                else (np.inf if action == 1 else 0)
            )

            trade_info_dict.update(
                {
                    "trigger_price": entry_price,
                    "action": "BUY" if action == 1 else "SELL",
                    "stop_loss_price": sl_price,
                }
            )

            future_df = group.loc[trigger_time + timedelta(minutes=1) :]

            # Check for SL and TP hit using vectorized operations
            sl_hit = future_df.loc[
                (action == 1) & (future_df["low"] <= sl_price)
                | (action == -1) & (future_df["high"] >= sl_price)
            ]
            tp_hit = future_df.loc[
                (action == 1) & (future_df["high"] >= target_price)
                | (action == -1) & (future_df["low"] <= target_price)
            ]

            # Determine exit condition
            if not sl_hit.empty and (tp_hit.empty or sl_hit.index[0] < tp_hit.index[0]):
                # Stop-loss hit first
                trade_info_dict["returns"] = -sl_pct
                trade_info_dict["stop_loss_time"] = sl_hit.index[0]
                trade_info_dict["target_time"] = np.nan
            elif not tp_hit.empty:
                # Take-profit hit first or end-of-day exit
                trade_info_dict["returns"] = (target_price / entry_price - 1) * action
                trade_info_dict["target_time"] = tp_hit.index[0]
                trade_info_dict["target_price"] = future_df.loc[
                    tp_hit.index[0], "close"
                ]
                trade_info_dict["stop_loss_time"] = np.nan
            else:
                # Neither SL or TP hit, exit at the end of the day
                trade_info_dict["returns"] = (
                    future_df.iloc[-1]["close"] / entry_price - 1
                ) * action
                trade_info_dict["target_time"] = future_df.index[-1]
                trade_info_dict["target_price"] = future_df.iloc[-1]["close"]
                trade_info_dict["stop_loss_time"] = np.nan

            all_entries_in_group.append(trade_info_dict)

        all_entries_in_group = pd.DataFrame(all_entries_in_group)
        if all_entries_in_group.empty:
            return all_entries_in_group
        all_entries_in_group["exit_time"] = all_entries_in_group[
            ["target_time", "stop_loss_time"]
        ].max(axis=1)

        return all_entries_in_group

    def backtest_intraday_trend(
        self,
        underlying: str,
        from_date: datetime | str = None,
        vix_df=None,
        open_nth=0,
        beta=1,
        fixed_trend_threshold=None,
        stop_loss=0.3,
        max_entries=3,
        rolling_days=60,
        randomize=False,
    ):
        index_prices = self.fetch_index_prices(underlying, from_timestamp=from_date)
        index_prices = prepare_index_prices_for_backtest(index_prices)

        if vix_df is None:
            vix_df = self.eod_client.get_data("VIX", return_columns=["open", "close"])

        vix = vix_df.copy()
        vix["open"] = vix["open"] * beta
        vix["close"] = vix["close"] * beta

        open_prices = (
            index_prices.groupby(index_prices["timestamp"].dt.date)
            .apply(lambda x: x.iloc[open_nth])
            .open.to_frame()
        )
        open_data = open_prices.merge(
            vix["open"].to_frame(),
            left_index=True,
            right_index=True,
            suffixes=("", "_vix"),
        )

        if randomize:
            fixed_trend_threshold = 0.0001

        open_data["threshold_movement"] = fixed_trend_threshold or (
            open_data["open_vix"] / 48
        )
        open_data["upper_bound"] = open_data["open"] * (
            1 + open_data["threshold_movement"] / 100
        )
        open_data["lower_bound"] = open_data["open"] * (
            1 - open_data["threshold_movement"] / 100
        )
        open_data["day_close"] = index_prices.groupby(
            index_prices["timestamp"].dt.date
        ).close.last()

        daily_minute_vols = index_prices.groupby(
            index_prices["timestamp"].dt.date
        ).apply(lambda x: x["close"].pct_change().abs().mean() * 100)

        daily_minute_vols_rolling = daily_minute_vols.rolling(
            rolling_days, min_periods=1
        ).mean()

        daily_open_to_close_trends = index_prices.open.groupby(
            index_prices["timestamp"].dt.date
        ).apply(lambda x: (x.iloc[-1] / x.iloc[0] - 1) * 100)

        daily_open_to_close_trends_rolling = (
            daily_open_to_close_trends.abs().rolling(rolling_days, min_periods=1).mean()
        )

        rolling_ratio = daily_open_to_close_trends_rolling / daily_minute_vols_rolling

        open_data.columns = [
            "day_open",
            "open_vix",
            "threshold_movement",
            "upper_bound",
            "lower_bound",
            "day_close",
        ]
        index_prices[
            [
                "day_open",
                "open_vix",
                "threshold_movement",
                "upper_bound",
                "lower_bound",
                "day_close",
            ]
        ] = open_data.loc[index_prices["timestamp"].dt.date].values
        index_prices["change_from_open"] = (
            (index_prices["close"] / index_prices["day_open"]) - 1
        ) * 100

        def calculate_daily_trade_data(group):
            """The group is a dataframe"""

            all_entries_in_a_day = {}
            # Find the first index where the absolute price change crosses the threshold
            entry = 1
            while entry <= max_entries:
                # Filtering the dataframe to only include the rows after open nth
                group = group.iloc[open_nth:]
                idx = group[
                    abs(group["change_from_open"]) >= group["threshold_movement"]
                ].first_valid_index()
                if idx is not None:  # if there is a crossing
                    result_dict = {
                        "returns": 0,
                        "trigger_time": np.nan,
                        "trigger_price": np.nan,
                        "trend_direction": np.nan,
                        "stop_loss_price": np.nan,
                        "stop_loss_time": np.nan,
                    }
                    # Record the price and time of crossing the threshold
                    cross_price = group.loc[idx, "close"]
                    cross_time = group.loc[idx, "timestamp"]

                    # Determine the direction of the movement
                    if randomize:
                        direction = np.random.choice([-1, 1])
                    else:
                        direction = np.sign(group.loc[idx, "change_from_open"])

                    # Calculate the stoploss price
                    if stop_loss == "dynamic":
                        # Selecting previous days rolling ratio
                        current_rolling_ratio = rolling_ratio.loc[
                            : cross_time.date()
                        ].iloc[-1]
                        # Calculating the stop_loss pct
                        if current_rolling_ratio > 30:
                            stop_loss_pct = 0.3
                        elif current_rolling_ratio < 10:
                            stop_loss_pct = 0.5
                        else:
                            stop_loss_pct = ((30 - current_rolling_ratio) / 100) + 0.3
                    else:
                        stop_loss_pct = stop_loss

                    stoploss_price = cross_price * (
                        1 - (stop_loss_pct / 100) * direction
                    )
                    result_dict.update(
                        {
                            "trigger_time": cross_time,
                            "trigger_price": cross_price,
                            "trend_direction": direction,
                            "stop_loss_price": stoploss_price,
                        }
                    )
                    future_prices = group.loc[idx:, "close"]

                    if (direction == 1 and future_prices.min() <= stoploss_price) or (
                        direction == -1 and future_prices.max() >= stoploss_price
                    ):  # Stop loss was breached
                        result_dict["returns"] = -stop_loss_pct
                        stoploss_time_idx = (
                            future_prices[
                                future_prices <= stoploss_price
                            ].first_valid_index()
                            if direction == 1
                            else future_prices[
                                future_prices >= stoploss_price
                            ].first_valid_index()
                        )
                        stoploss_time = group.loc[stoploss_time_idx, "timestamp"]
                        result_dict["stop_loss_time"] = stoploss_time
                        all_entries_in_a_day[f"entry_{entry}"] = result_dict
                        group = group.loc[stoploss_time_idx:]
                        entry += 1
                    else:  # Stop loss was not breached
                        if direction == 1:
                            result_dict["returns"] = (
                                (group["close"].iloc[-1] - cross_price) / cross_price
                            ) * 100
                        else:
                            result_dict["returns"] = (
                                (group["close"].iloc[-1] - cross_price) / cross_price
                            ) * -100
                        all_entries_in_a_day[f"entry_{entry}"] = result_dict
                        break
                else:
                    break

            all_entries_in_a_day["total_returns"] = sum(
                [v["returns"] for v in all_entries_in_a_day.values()]
            )
            return all_entries_in_a_day

        # Applying the function to each day's worth of data
        returns = index_prices.groupby(index_prices["timestamp"].dt.date).apply(
            calculate_daily_trade_data
        )
        returns = returns.to_frame()
        returns.index = pd.to_datetime(returns.index)
        returns.columns = ["trade_data"]

        # merging with open_data
        merged = returns.merge(open_data, left_index=True, right_index=True)
        merged["total_returns"] = merged["trade_data"].apply(
            lambda x: x["total_returns"]
        )

        merged["predicted_trend"] = merged.trade_data.apply(
            lambda x: x.get("entry_1", {}).get("trend_direction", None)
        )

        # calculating prediction accuracy
        merged["actual_trend"] = daily_open_to_close_trends.apply(np.sign)
        merged["trend_match"] = merged.predicted_trend == merged.actual_trend
        merged["rolling_prediction_accuracy"] = (
            merged[~pd.isna(merged.predicted_trend)]
            .trend_match.expanding(min_periods=1)
            .mean()
        )
        merged["rolling_prediction_accuracy"] = merged[
            "rolling_prediction_accuracy"
        ].fillna(method="ffill")

        merged = nav_drawdown_analyser(
            merged, column_to_convert="total_returns", profit_in_pct=True
        )

        # calculating the minute vol
        merged["minute_vol"] = daily_minute_vols

        # calculating the open to close trend
        merged["open_to_close_trend"] = daily_open_to_close_trends

        merged["open_to_close_trend_abs"] = merged["open_to_close_trend"].abs()

        # calculating the ratio and rolling mean
        merged["minute_vol_rolling"] = daily_minute_vols_rolling
        merged["open_to_close_trend_rolling"] = daily_open_to_close_trends_rolling
        merged["ratio"] = merged["open_to_close_trend_abs"] / merged["minute_vol"]
        merged["rolling_ratio"] = rolling_ratio

        return merged


def generate_cte_entries(
    dataframe: pd.DataFrame,
    timestamp_col: str,
    strike_col: str,
    expiry_col: str,
    option_type: str,
):
    cte_entries = [
        f"('{row[timestamp_col]}'::timestamp, {row[strike_col]}::integer, '{row[expiry_col]}'::text, '{option_type}'::text)"
        for _, row in dataframe.iterrows()
    ]
    return cte_entries


def generate_cte_entries_from_df(dataframe: pd.DataFrame) -> list:
    cte_entries = []

    for col in dataframe.columns:
        if "strike" in col:
            # Determine option type
            option_type = "CE" if "call" in col else "PE"

            # Determine the correct timestamp and expiry columns
            if "square_up" in col:
                timestamp_col = "square_up_timestamp"
                expiry_col = "square_up_expiry"
            else:
                timestamp_col = "timestamp"
                expiry_col = "expiry"

            # Generate CTE entries
            entries = generate_cte_entries(
                dataframe, timestamp_col, col, expiry_col, option_type
            )
            cte_entries.extend(entries)

    return cte_entries


def convert_cte_entries_to_query(
    cte_entries: list,
    underlying: str,
    cols_to_return: list | None = None,
) -> text:
    if cols_to_return is None:
        cols_to_return = ["timestamp", "expiry", "strike", "option_type", "close"]

    # Join the entries with a comma to create a single string
    cte_entries_str = ", ".join(cte_entries)
    columns_str = ", ".join([f"index_options.{x}" for x in cols_to_return])

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
        WHERE index_options.underlying = '{underlying}';
        """
    )

    return sql_query


def add_strikes(
    underlying: UnderlyingInfo,
    df: pd.DataFrame,
    strike_offset: float = 0,
    call_strike_offset: float | None = None,
    put_strike_offset: float | None = None,
):
    df = df.copy()

    # Setting the strikes
    if call_strike_offset is None:
        call_strike_offset = strike_offset
    if put_strike_offset is None:
        put_strike_offset = strike_offset

    df["call_strike"] = df.open.apply(
        lambda x: find_strike(x * (1 + call_strike_offset), underlying.base)
    )
    df["put_strike"] = df.open.apply(
        lambda x: find_strike(x * (1 - put_strike_offset), underlying.base)
    )

    return df


def rearrange_options_prices(prices: pd.DataFrame) -> pd.DataFrame:
    """Used on the output of fetch_option_prices of the database to rearrange the columns"""
    option_prices = (
        prices.groupby(["timestamp", "expiry", "strike", "option_type"])
        .close.first()
        .unstack(level="option_type")
        .reset_index()
    )
    option_prices.index.name = None
    option_prices.columns.name = None
    option_prices.set_index("timestamp", inplace=True)
    return option_prices.sort_index()


def melt_frame(
    trade_df: pd.DataFrame,
    leg_type: str,
    square_up: bool,
) -> pd.DataFrame:
    timestamp_col = "square_up_timestamp" if square_up else "timestamp"
    expiry_col = "square_up_expiry" if square_up else "expiry"
    leg_cols = [
        col for col in trade_df.columns if f"{leg_type}" in col and "strike" in col
    ]
    melted_df = pd.melt(
        trade_df,
        ["trade_id", timestamp_col, expiry_col],
        leg_cols,
        f"{leg_type}_leg",
        f"strike",
    )

    melted_df[f"{leg_type}_leg"] = melted_df[f"{leg_type}_leg"].str.replace(
        "_strike", ""
    )

    return melted_df


def merge_with_option_prices(
    melted_df: pd.DataFrame,
    option_prices_df: pd.DataFrame,
    leg_type: str,
    square_up: bool,
) -> pd.DataFrame:
    """
    Merge the melted legs data with the option prices dataframe.
    """
    price_column = f"{leg_type}_price"
    timestamp_col = "square_up_timestamp" if square_up else "timestamp"
    expiry_col = "square_up_expiry" if square_up else "expiry"
    if square_up:
        option_prices_df = option_prices_df.rename(
            columns={
                "timestamp": "square_up_timestamp",
                "expiry": "square_up_expiry",
            }
        )

    return pd.merge(
        melted_df,
        option_prices_df[[timestamp_col, expiry_col, "strike", price_column]],
        left_on=[timestamp_col, expiry_col, "strike"],
        right_on=[timestamp_col, expiry_col, "strike"],
        how="left",
    )


def pivot_frame(
    merged_df: pd.DataFrame,
    leg_type: str,
    square_up: bool,
) -> pd.DataFrame:
    timestamp_col = "square_up_timestamp" if square_up else "timestamp"
    expiry_col = "square_up_expiry" if square_up else "expiry"

    pivoted = merged_df.pivot_table(
        index=["trade_id", timestamp_col, expiry_col],
        columns=f"{leg_type}_leg",
        values=[f"strike", f"{leg_type}_price"],
        aggfunc="first",
    )

    pivoted = pivoted.rename(columns={f"{leg_type}_price": "price"})

    pivoted.columns = [
        f"{col[1]}_{col[0]}" if col[0] in ["strike", "price"] else col[1]
        for col in pivoted.columns.values
    ]
    return pivoted.reset_index()


def add_option_prices_to_leg(trade_df, option_prices_df, leg_type, square_up=False):
    """
    A generalized function to process either trade or square-up legs.
    """
    if square_up:
        trade_df = trade_df.filter(regex="^square_up_|^trade_id$")
    else:
        # Filter out square-up columns
        trade_df = trade_df.filter(regex="^(?!square_up_)")

    legs_df = melt_frame(trade_df, leg_type, square_up)

    merged_df = merge_with_option_prices(legs_df, option_prices_df, leg_type, square_up)

    return pivot_frame(merged_df, leg_type, square_up)


def populate_with_option_prices(trade_df, option_prices_df, has_square_up=False):
    """
    Refactored function to process trade data and merge with option prices. The trade_df should
    contain the following columns:
    - trade_id
    - timestamp
    - expiry
    and call and put strike columns.
    """
    call_trades = add_option_prices_to_leg(trade_df, option_prices_df, "call")
    put_trades = add_option_prices_to_leg(trade_df, option_prices_df, "put")
    merged_trades = call_trades.merge(
        put_trades, on=["trade_id", "timestamp", "expiry"], how="left"
    )
    if not has_square_up:
        return merged_trades

    square_up_call_trades = add_option_prices_to_leg(
        trade_df, option_prices_df, "call", True
    )
    square_up_put_trades = add_option_prices_to_leg(
        trade_df, option_prices_df, "put", True
    )
    square_up_trades = square_up_call_trades.merge(
        square_up_put_trades,
        on=["trade_id", "square_up_timestamp", "square_up_expiry"],
        how="left",
    )
    merged_with_square_up = merged_trades.merge(
        square_up_trades,
        on=["trade_id"],
        how="left",
    )
    return merged_with_square_up


def generate_sample_skeleton(with_square_up=False, hedge_leg=None):
    """For testing purposes only"""
    # Sample data for Skeleton DataFrame
    # Timestamps
    timestamps = pd.date_range(start="2023-01-01", periods=10, freq="D")

    # Expiry dates, let's assume they are weekly
    expiries = pd.date_range(start="2023-01-10", periods=2, freq="W")

    # Strike prices
    call_strikes = np.linspace(100, 110, 3)
    put_strikes = np.linspace(100, 110, 3)

    # Creating a grid of all combinations
    skeleton_data = pd.MultiIndex.from_product(
        [timestamps, expiries, zip(call_strikes, put_strikes)],
        names=["timestamp", "expiry", "strikes"],
    ).to_frame(index=False)
    skeleton_data.drop_duplicates(subset=["timestamp"], inplace=True, keep="first")
    skeleton_data["call_strike"] = skeleton_data["strikes"].apply(lambda x: x[0])
    skeleton_data["put_strike"] = skeleton_data["strikes"].apply(lambda x: x[1])
    skeleton_data.drop(columns=["strikes"], inplace=True)

    if hedge_leg:
        skeleton_data[f"{hedge_leg}_hedge_strike"] = (
            skeleton_data[f"{hedge_leg}_strike"] + 5
            if hedge_leg == "call"
            else skeleton_data[f"{hedge_leg}_strike"] - 5
        )

    if with_square_up:
        # Adding square up columns to the skeleton data
        skeleton_data["square_up_timestamp"] = skeleton_data["timestamp"]
        skeleton_data["square_up_expiry"] = skeleton_data["expiry"].shift(1)
        skeleton_data["square_up_call_strike"] = skeleton_data["call_strike"].shift(1)
        skeleton_data["square_up_put_strike"] = skeleton_data["put_strike"].shift(1)
        if hedge_leg:
            skeleton_data[f"square_up_{hedge_leg}_hedge_strike"] = skeleton_data[
                f"{hedge_leg}_hedge_strike"
            ].shift(1)
    skeleton_data["trade_id"] = range(1, len(skeleton_data) + 1)
    return skeleton_data


def generate_sample_option_prices():
    """For testing purposes only"""
    timestamps = pd.date_range(start="2023-01-01", periods=10, freq="D")

    expiries = pd.date_range(start="2023-01-10", periods=2, freq="W")

    option_df_strikes = np.arange(90, 150, 5)
    option_prices_data = pd.MultiIndex.from_product(
        [timestamps, expiries, option_df_strikes],
        names=["timestamp", "expiry", "strike"],
    ).to_frame(index=False)
    option_prices_data["call_price"] = np.random.uniform(5, 15, len(option_prices_data))
    option_prices_data["put_price"] = np.random.uniform(3, 10, len(option_prices_data))

    return option_prices_data


def calculate_intrinsic_value(df, open_col, strike_col, call=True):
    """Calculate the intrinsic value for options."""
    if call:
        return np.maximum(0, df[open_col] - df[strike_col])
    else:
        return np.maximum(0, df[strike_col] - df[open_col])


def calculate_option_price(
    df, open_col, strike_col, time_to_expiry_col, iv_col, call=True
):
    """Calculate the option price using a model (e.g., Black-Scholes)."""
    if call:
        return call(
            df[open_col], df[strike_col], df[time_to_expiry_col], 0.05, df[iv_col]
        )
    else:
        return put(
            df[open_col], df[strike_col], df[time_to_expiry_col], 0.05, df[iv_col]
        )


def fill_option_prices(
    df, price_col, strike_col, time_to_expiry_col, iv_col, open_col, call=True
):
    """Fill missing option prices in the DataFrame."""
    short_expiry = df[time_to_expiry_col] < (0.5 / (364 * 24))
    intrinsic = calculate_intrinsic_value(df, open_col, strike_col, call)
    option_price = calculate_option_price(
        df, open_col, strike_col, time_to_expiry_col, iv_col, call
    )

    df[price_col] = np.where(
        df[price_col].isna() & short_expiry,
        intrinsic,
        np.where(df[price_col].isna(), option_price, df[price_col]),
    )
    return df


def fill_missing_option_prices(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Fill regular call and put prices
    df = fill_option_prices(
        df, "call_price", "call_strike", "time_to_expiry", "iv", "open", call=True
    )
    df = fill_option_prices(
        df, "put_price", "put_strike", "time_to_expiry", "iv", "open", call=False
    )

    # Fill square up call and put prices
    df = fill_option_prices(
        df,
        "square_up_call_price",
        "square_up_call_strike",
        "square_up_time_to_expiry",
        "iv",
        "open",
        call=True,
    )
    df = fill_option_prices(
        df,
        "square_up_put_price",
        "square_up_put_strike",
        "square_up_time_to_expiry",
        "iv",
        "open",
        call=False,
    )

    return df
