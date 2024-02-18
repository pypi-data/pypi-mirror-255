import pandas as pd
from pandas.core.groupby import DataFrameGroupBy
from datetime import datetime, time
from volstreet.utils.core import find_strike
from volstreet.backtests.tools import prepare_index_prices_for_backtest
from volstreet.backtests.framework import (
    rearrange_options_prices,
    populate_with_option_prices,
    Signal,
    generate_cte_entries_from_df,
    convert_cte_entries_to_query,
)
from volstreet.backtests.framework import BackTester
from volstreet.backtests.underlying_info import UnderlyingInfo


class TrendBackTest(BackTester):
    def __init__(self, underlying: UnderlyingInfo):
        self.underlying = underlying
        self.meta_data = {}
        super().__init__()

    @staticmethod
    def generate_bounds(
        index_prices: pd.DataFrame,
        vix_df: pd.DataFrame | None = None,
        beta: float = 1.0,
        open_nth: int = 0,
        fixed_trend_threshold: float | None = None,
        randomize: bool = False,
    ):
        index_prices = index_prices.copy()

        if not isinstance(index_prices.index, pd.DatetimeIndex):
            index_prices = index_prices.set_index("timestamp")

        open_data = (
            index_prices.groupby(index_prices.index.date)
            .apply(lambda x: x.iloc[open_nth])
            .open.to_frame()
        )

        if fixed_trend_threshold:
            trend_threshold = fixed_trend_threshold
            open_data["threshold_movement"] = trend_threshold
        elif randomize:
            trend_threshold = 0.0001
            open_data["threshold_movement"] = trend_threshold
        else:
            if vix_df is None:
                raise ValueError(
                    "vix_df must be provided if fixed_trend_threshold is not provided"
                )
            vix = vix_df.copy()
            vix["open"] = vix["open"] * beta
            vix["close"] = vix["close"] * beta
            trend_threshold = vix["open"] / 48
            open_data["threshold_movement"] = trend_threshold.loc[
                open_data.index
            ].values

        open_data["threshold_movement"] = trend_threshold

        open_data["upper_bound"] = open_data["open"] * (
            1 + open_data["threshold_movement"] / 100
        )
        open_data["lower_bound"] = open_data["open"] * (
            1 - open_data["threshold_movement"] / 100
        )
        open_data["day_close"] = index_prices.groupby(
            index_prices.index.date
        ).close.last()

        # Now to extend the bounds to every entry of the index prices of each day
        open_data = open_data.reindex(index_prices.index, method="ffill")

        return open_data[["upper_bound", "lower_bound"]]

    @staticmethod
    def generate_triggers(
        underlying_price_dataframe: pd.DataFrame,
        bounds: pd.DataFrame,
        target_column: str = "open",
    ):
        # Ensure required columns are present
        if not all(col in bounds.columns for col in ["upper_bound", "lower_bound"]):
            raise ValueError(
                "Bounds dataframe must have 'upper_bound' and 'lower_bound' columns"
            )

        def generate_cross_signal(bound, signal_type):
            """Helper function to generate signal data based on the bound."""
            condition = (
                underlying_price_dataframe[target_column] > bound
                if signal_type == Signal.BUY
                else underlying_price_dataframe[target_column] < bound
            )
            crosses = underlying_price_dataframe.loc[
                condition, target_column
            ].to_frame()
            crosses["signal"] = signal_type
            return crosses

        # Generate signals for upper and lower bounds
        crosses_upper = generate_cross_signal(bounds["upper_bound"], Signal.BUY)
        crosses_lower = generate_cross_signal(bounds["lower_bound"], Signal.SELL)

        # Combine and return the result
        combined = pd.concat([crosses_upper, crosses_lower]).sort_index()
        combined.rename(columns={target_column: "entry_price"}, inplace=True)
        return combined

    @staticmethod
    def find_exit_info(signal, forward_looking_df, target_column, stop_loss_price):
        """Internal use function. Find the exit information based on the forward looking dataframe."""
        if signal == Signal.BUY:
            trigger_condition = forward_looking_df[target_column] < stop_loss_price
        else:  # Signal.SELL
            trigger_condition = forward_looking_df[target_column] > stop_loss_price

        stop_loss_triggered = forward_looking_df[trigger_condition].first_valid_index()

        if stop_loss_triggered:
            exit_time = stop_loss_triggered
            exit_type = "stop_loss"
        else:
            exit_time = forward_looking_df.index[-1]
            exit_type = "day_close"

        exit_price = forward_looking_df.loc[exit_time, target_column]
        return exit_time, exit_price, exit_type

    def cash_backtest(
        self,
        triggers: pd.DataFrame,
        underlying_df_grouped: DataFrameGroupBy,
        stop_loss: float = 0.3,
        target_column: str = "entry_price",
    ) -> pd.DataFrame:
        """Function that essentially runs the backtest by adding exit info
        to the signals dataframe."""

        def calculate_stop_loss_price(signal, price, stop_loss):
            """Internal use function. Calculate stop loss price based on signal and current price."""
            return (
                price * (1 - stop_loss / 100)
                if signal == Signal.BUY
                else price * (1 + stop_loss / 100)
            )

        triggers = triggers.copy()
        triggers["stop_loss"] = triggers.apply(
            lambda row: calculate_stop_loss_price(
                row["signal"], row[target_column], stop_loss
            ),
            axis=1,
        )

        results = []
        processed_triggers = []
        previous_exit_time = datetime.min

        for index, row in triggers.iterrows():
            current_trigger_time = index

            # Skip triggers that occur before the exit time of the previous trigger
            if (
                current_trigger_time < previous_exit_time
                or current_trigger_time.time() >= time(15, 20)
            ):
                continue

            day = current_trigger_time.date()

            forward_looking_df = underlying_df_grouped.get_group(day).loc[
                current_trigger_time:
            ][1:]

            # Hygiene check to see if the trigger is close to the end of the day
            if len(forward_looking_df) < 5:
                continue

            exit_time, exit_price, exit_type = self.find_exit_info(
                row["signal"], forward_looking_df, "open", row["stop_loss"]
            )
            profit = (
                exit_price - row[target_column]
                if row["signal"] == Signal.BUY
                else row[target_column] - exit_price
            )
            previous_exit_time = exit_time

            results.append([exit_time, exit_price, exit_type, profit])
            processed_triggers.append(index)

        triggers[
            ["square_up_timestamp", "exit_price", "exit_type", "profit"]
        ] = pd.DataFrame(
            results,
            columns=["exit_time", "exit_price", "exit_type", "profit"],
            index=processed_triggers,
        )

        return triggers.dropna()

    @staticmethod
    def split_trades_by_signal(
        cash_backtest: pd.DataFrame,
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        buy_trades = cash_backtest[cash_backtest.signal == Signal.BUY]
        sell_trades = cash_backtest[cash_backtest.signal == Signal.SELL]
        return buy_trades, sell_trades

    def modify_trades_for_execution(
        self,
        trades_by_signal: pd.DataFrame,
        signal: Signal,
        underlying_info: UnderlyingInfo,
        hedge_offset: float | None = None,
    ) -> pd.DataFrame:
        """Entire dataframe consists of a single signal type. This function prepares the dataframe for merging with the main dataframe. We lose meta data about the trades here. Devise a mechanism to store that information."""

        trades_by_signal = trades_by_signal.copy()

        # Vectorized strike calculation
        atm_strike = trades_by_signal["entry_price"].apply(
            lambda n: find_strike(n, self.underlying.base)
        )
        trades_by_signal["call_strike"] = atm_strike
        trades_by_signal["put_strike"] = atm_strike
        trades_by_signal["expiry"] = trades_by_signal.index.map(
            lambda d: self.fetch_nearest_expiry_from_date(self.underlying.name, d)
        )
        trades_by_signal["expiry"] = trades_by_signal["expiry"].apply(
            lambda d: d.strftime("%d%b%y").upper()
        )

        if hedge_offset:
            hedge_type = "call" if signal == Signal.BUY else "put"
            offset_multiplier = (
                1 + hedge_offset if signal == Signal.BUY else 1 - hedge_offset
            )
            hedge_strike = trades_by_signal["entry_price"].apply(
                lambda n: find_strike(n * offset_multiplier, underlying_info.base)
            )
            # Rename hedge columns conditionally based on the signal
            trades_by_signal[f"{hedge_type}_hedge_strike"] = hedge_strike

        # Square up info
        for col_name in [
            col
            for col in trades_by_signal.columns
            if "strike" in col or "expiry" in col
        ]:
            trades_by_signal[f"square_up_{col_name}"] = trades_by_signal[col_name]

        filtered = trades_by_signal.filter(regex="trade_id|strike|expiry|square_up")
        meta_data = trades_by_signal.filter(regex=r"^(?!.*strike|expiry|square_up).*$")
        meta_data = meta_data.rename(columns={"profit": "cash_profit"})

        self.meta_data[signal] = meta_data

        return filtered.reset_index()

    def run_cash_backtest(
        self,
        from_date: str | datetime = "2019-04-01",
        to_date: str | datetime = None,
        start_after: tuple[int, int] = (9, 15),
        end_before: tuple[int, int] = (15, 20),
        open_candle: int = 0,
        beta: float = 1.0,
        fixed_trend_threshold: float | None = None,
        randomize: bool = False,
        stop_loss: float = 0.3,
    ):
        index_prices = self.fetch_index_prices(self.underlying.name, from_date, to_date)
        index_prices = prepare_index_prices_for_backtest(
            index_prices, start_after, end_before
        )
        index_prices.set_index("timestamp", inplace=True)

        if randomize or fixed_trend_threshold:
            vix_data = None
        else:
            vix_data = self.eod_client.get_data(
                "VIX", return_columns=["open", "close"], from_date=f"{from_date}"
            )

        bounds = self.generate_bounds(
            index_prices, vix_data, beta, open_candle, fixed_trend_threshold, randomize
        )
        triggers = self.generate_triggers(index_prices, bounds)
        cash_backtest = self.cash_backtest(
            triggers, index_prices.groupby(index_prices.index.date), stop_loss=stop_loss
        )

        return cash_backtest

    def process_trades(
        self,
        trades: pd.DataFrame,
        trade_signal: Signal,
        with_hedge: bool = True,
    ):
        # Generate CTE entries and convert to query
        cte_entries = generate_cte_entries_from_df(trades)
        query = convert_cte_entries_to_query(cte_entries, self.underlying.name)

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

        # Calculate additional columns
        trades_with_prices["synthetic_entry_price"] = (
            trades_with_prices["call_strike"]
            + trades_with_prices["call_price"]
            - trades_with_prices["put_price"]
        )
        trades_with_prices["synthetic_square_up_price"] = (
            trades_with_prices["square_up_call_strike"]
            + trades_with_prices["square_up_call_price"]
            - trades_with_prices["square_up_put_price"]
        )

        if trade_signal == Signal.BUY:
            trades_with_prices["synthetic_profit"] = (
                trades_with_prices["synthetic_square_up_price"]
                - trades_with_prices["synthetic_entry_price"]
            )
        else:
            trades_with_prices["synthetic_profit"] = (
                trades_with_prices["synthetic_entry_price"]
                - trades_with_prices["synthetic_square_up_price"]
            )

        if with_hedge:
            hedge_column = "call" if trade_signal == Signal.BUY else "put"
            trades_with_prices["hedge_profit"] = (
                trades_with_prices[f"{hedge_column}_hedge_price"]
                - trades_with_prices[f"square_up_{hedge_column}_hedge_price"]
            )
        else:
            trades_with_prices["hedge_profit"] = 0

        trades_with_prices["strategy_profit"] = (
            trades_with_prices["synthetic_profit"] + trades_with_prices["hedge_profit"]
        )

        # Merge with meta data
        trades_final = self.meta_data[trade_signal].merge(
            trades_with_prices, on="trade_id"
        )

        return trades_final

    def run_option_backtest(
        self,
        cash_backtest: pd.DataFrame | None = None,
        from_date: str | datetime = None,
        to_date: str | datetime = None,
        start_after: tuple[int, int] = (9, 15),
        end_before: tuple[int, int] = (15, 20),
        open_candle: int = 0,
        beta: float = 1.0,
        fixed_trend_threshold: float | None = None,
        randomize: bool = False,
        stop_loss: float = 0.3,
        hedge_offset: float | None = None,
    ):
        if cash_backtest is None:
            cash_backtest = self.run_cash_backtest(
                from_date,
                to_date,
                start_after,
                end_before,
                open_candle,
                beta,
                fixed_trend_threshold,
                randomize,
                stop_loss,
            )

        cash_backtest["trade_id"] = range(1, len(cash_backtest) + 1)

        buy_trades, sell_trades = self.split_trades_by_signal(cash_backtest)

        buy_trades = self.modify_trades_for_execution(
            buy_trades, Signal.BUY, self.underlying, hedge_offset
        )
        sell_trades = self.modify_trades_for_execution(
            sell_trades, Signal.SELL, self.underlying, hedge_offset
        )
        with_hedge = True if hedge_offset else False

        buy_trades_final = self.process_trades(buy_trades, Signal.BUY, with_hedge)
        sell_trades_final = self.process_trades(sell_trades, Signal.SELL, with_hedge)

        full_final = pd.concat([buy_trades_final, sell_trades_final])
        full_final.sort_values("trade_id", inplace=True)
        full_final.set_index("timestamp", inplace=True)
        return full_final
