import numpy as np
import pandas as pd
import os
from datetime import datetime, time
from collections import defaultdict
from volstreet.config import logger
from volstreet import blackscholes as bs
from volstreet.vectorized_blackscholes import add_greeks_to_dataframe
from volstreet.backtests.underlying_info import UnderlyingInfo
from volstreet.backtests.intraday_backtest_abc import IntradayBackTest
from volstreet.parallelization import execute_in_parallel
from volstreet.trade_interface.blocks import OptionType
from volstreet.utils.data_io import make_directory_if_needed


class DeltaBackTest(IntradayBackTest):
    RESULTS_FOLDER = "data\\delta_backtests\\"

    def __init__(self, underlying: UnderlyingInfo):
        super().__init__(underlying)
        self.rolling_atm_info = None

    def get_strike_columns(self):
        return ["call_strike", "put_strike"]

    def merge_with_option_prices(
        self,
        data_frame_to_merge: pd.DataFrame,
    ) -> pd.DataFrame:
        option_prices = self.option_prices.reset_index()

        merged_with_call_prices = data_frame_to_merge.merge(
            option_prices[["timestamp", "expiry", "call_price", "strike"]],
            left_on=["timestamp", "expiry", "call_strike"],
            right_on=["timestamp", "expiry", "strike"],
            how="left",
        )
        merged_with_put_prices = merged_with_call_prices.merge(
            option_prices[["timestamp", "expiry", "put_price", "strike"]],
            left_on=["timestamp", "expiry", "put_strike"],
            right_on=["timestamp", "expiry", "strike"],
            how="left",
        )
        merged_with_put_prices.drop(columns=["strike_x", "strike_y"], inplace=True)

        strike_columns = [
            col for col in merged_with_put_prices.columns if "strike" in col
        ]
        strike_type = {col: int for col in strike_columns}

        merged_with_put_prices.dropna(subset=strike_columns, inplace=True)

        merged_with_put_prices = merged_with_put_prices.astype(
            {**strike_type, "call_price": float, "put_price": float, "open": float}
        )

        return merged_with_put_prices

    def store_atm_info(self, intraday_prices: pd.DataFrame):
        intraday_prices = self._build_option_chain_skeleton(
            self.underlying.name,
            intraday_prices,
            num_strikes=1,
            num_exp=1,
            threshold_days_expiry=0,
        )
        with_option_prices = self.merge_with_option_prices(intraday_prices)
        rolling_atm_info = with_option_prices[
            [
                "timestamp",
                "open",
                "time_to_expiry",
                "call_strike",
                "put_strike",
                "call_price",
                "put_price",
            ]
        ]

        rolling_atm_info.columns = [
            "atm_" + col if (("call" in col) or ("put" in col)) else col
            for col in rolling_atm_info.columns
        ]
        self.rolling_atm_info = rolling_atm_info

    def add_greeks_to_rolling_atm_info(self):
        temp_df = self.rolling_atm_info.copy()
        temp_df.columns = [col.replace("atm_", "") for col in temp_df.columns]
        # remove temp_df = temp_df.astype({"open": float, "call_strike": int, "put_strike": int})
        self.rolling_atm_info = add_greeks_to_dataframe(
            temp_df, r_col="r", use_one_iv=False
        )

    def calculate_moving_interest_rate(self) -> pd.DataFrame:
        with_option_prices = self.rolling_atm_info.copy()
        with_option_prices["synthetic_rate"] = (
            with_option_prices["atm_call_strike"]
            + with_option_prices["atm_call_price"]
            - with_option_prices["atm_put_price"]
        )
        with_option_prices["r"] = (
            (with_option_prices["synthetic_rate"] / with_option_prices["open"]) - 1
        ) * (1 / with_option_prices["time_to_expiry"])

        # Removing infinities
        with_option_prices["r"] = np.where(
            with_option_prices["r"] == np.inf,
            50,
            np.where(with_option_prices["r"] == -np.inf, -50, with_option_prices["r"]),
        )
        self.rolling_atm_info["r"] = with_option_prices["r"]
        return with_option_prices[["timestamp", "r"]]

    @staticmethod
    def find_closest_deltas(
        strikes: pd.DataFrame,
        target: float,
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        delta_col = "call_delta" if "call_delta" in strikes.columns else "put_delta"
        lower_strike = strikes[strikes[delta_col] <= target].nlargest(1, delta_col)
        upper_strike = strikes[strikes[delta_col] >= target].nsmallest(1, delta_col)
        if lower_strike.empty:
            lower_strike = (
                upper_strike.copy()
            )  # Crucial to copy the dataframe here because we assign a new column later
            # And want to avoid overwriting the original dataframe
        if upper_strike.empty:
            upper_strike = (
                lower_strike.copy()
            )  # Crucial to copy the dataframe here because we assign a new column later
            # And want to avoid overwriting the original dataframe
        return lower_strike, upper_strike

    @staticmethod
    def calculate_ratios(
        lower: pd.DataFrame,
        upper: pd.DataFrame,
        target: float,
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        col = "call_delta" if "call_delta" in lower.columns else "put_delta"
        lower_delta = lower[col].iloc[0]
        upper_delta = upper[col].iloc[0]
        lower_strike = lower["strike"].iloc[0]
        upper_strike = upper["strike"].iloc[0]

        if lower_strike == upper_strike:
            ratio_lower = 0.5
            ratio_upper = 0.5
        else:
            ratio_lower = (upper_delta - target) / (upper_delta - lower_delta)
            ratio_upper = (target - lower_delta) / (upper_delta - lower_delta)

        lower["ratio"] = round(ratio_lower, 2)
        upper["ratio"] = round(ratio_upper, 2)

        return lower, upper

    def calculate_strikes_and_ratios(
        self,
        option_chain: pd.DataFrame,
        delta_range: tuple,
        target_delta: float,
    ) -> dict[str, list[tuple]] | bool:
        """New function to calculate strikes and ratios for a given delta range and target delta.
        In run_day this will be used to add strikes to the segment"""

        if not (delta_range[0] <= target_delta <= delta_range[1]):
            raise ValueError("Target delta must be within the specified delta range.")

        def filter_and_sort_options(options, delta_col):
            filtered_options = options[options[delta_col] >= delta_range[0]]
            filtered_options = filtered_options[
                filtered_options[delta_col] <= delta_range[1]
            ]
            return filtered_options[["strike", delta_col]].sort_values(by=delta_col)

        def find_best_strike(options, delta):
            col = "call_delta" if "call_delta" in options.columns else "put_delta"
            close_strikes = options[np.abs(options[col] - delta) <= 0.01]
            if not close_strikes.empty:
                return close_strikes.iloc[0]
            return None

        def process_option_type(options, delta, option_type):
            best_option = find_best_strike(options, delta)
            if best_option is not None:
                _target_delta = best_option[f"{option_type}_delta"]
                positions = [
                    [best_option[f"strike"]] * 2,
                    [0.5] * 2,
                ]
                return _target_delta, positions

            lower_delta, upper_delta = self.find_closest_deltas(options, delta)
            ratios = self.calculate_ratios(lower_delta, upper_delta, delta)
            weighted_average_delta = sum(
                [(df.ratio * df[f"{option_type}_delta"]).values[0] for df in ratios]
            )
            trade_options = [
                strike_df[["strike", "ratio"]].values.tolist()[0]
                for strike_df in ratios
            ]
            trade_options = [*zip(*trade_options)]
            return weighted_average_delta, trade_options

        option_chain["put_delta"] = np.abs(option_chain["put_delta"])

        calls = filter_and_sort_options(option_chain, "call_delta")
        puts = filter_and_sort_options(option_chain, "put_delta")

        # Hygiene dropping of delta == 0 options
        calls = calls[calls["call_delta"] != 0].copy()
        puts = puts[puts["put_delta"] != 0].copy()

        trade_dict = {}
        call_delta, call_options = process_option_type(calls, target_delta, "call")
        put_delta, put_options = process_option_type(puts, target_delta, "put")

        if abs(call_delta - put_delta) > 0.05:
            return False

        trade_dict["calls"] = call_options
        trade_dict["puts"] = put_options

        return trade_dict

    def select_equal_strikes(
        self,
        snapshot: pd.DataFrame,
        trade_deltas_between: tuple[float, float],
    ) -> tuple[int, int]:
        """Old function to select equal strikes. This is used in run_day before multi strike
        to select strikes for the segment."""

        def filter_and_process(
            df_with_greeks: pd.DataFrame, deltas_range: tuple[float, float]
        ) -> pd.DataFrame:
            df = df_with_greeks.copy()
            # Filtering for strikes with deltas within the given range
            filtered_df = df[
                (df["call_delta"] > deltas_range[0])
                & (df["call_delta"] < deltas_range[1])
                & (df["put_delta"] > deltas_range[0])
                & (df["put_delta"] < deltas_range[1])
            ]
            return filtered_df

        with_option_prices = self.merge_with_option_prices(snapshot)
        with_greeks = add_greeks_to_dataframe(with_option_prices, r_col="r")
        with_greeks["put_delta"] = np.abs(with_greeks["put_delta"])

        filtered = filter_and_process(with_greeks, trade_deltas_between)

        if filtered.empty:
            logger.info(
                f"No strikes found in the given delta range {trade_deltas_between}. "
                f"Trying to find strikes in the range (0.22, 0.78)"
            )
            filtered = filter_and_process(
                with_greeks, (0.22, 0.78)
            )  # Hardcoded fallback

        if filtered.empty:
            raise ValueError(
                "No strikes found in the given delta range. Handle this error by shifting the range or "
                "by advancing in time."
            )

        # Creating a DataFrame with all combinations of Call and Put strikes
        call_strikes = filtered["call_strike"].repeat(len(filtered))
        put_strikes = np.tile(filtered["put_strike"], len(filtered))
        call_deltas = filtered["call_delta"].repeat(len(filtered)).values
        put_deltas = np.tile(filtered["put_delta"], len(filtered))

        # Calculate disparities using vectorized operations
        disparities = np.maximum(call_deltas, put_deltas) / np.minimum(
            call_deltas, put_deltas
        )
        # Creating the final DataFrame
        combined_df = pd.DataFrame(
            {
                "call_strike": call_strikes,
                "put_strike": put_strikes,
                "disparity": disparities,
            },
        )
        combined_df = combined_df.reset_index(drop=True)
        if combined_df.empty:
            return self.select_equal_strikes(snapshot, (0.25, 0.75))
        most_equal_strike = combined_df.loc[combined_df["disparity"].idxmin()]
        return most_equal_strike["call_strike"], most_equal_strike["put_strike"]

    def prepare_positions(
        self,
        segment_prices: pd.DataFrame,
        delta_range: tuple[float, float],
        target_delta: float,
    ):
        """
        At this point the segment has been prepared with "r" and "time_to_expiry" columns.
        Prepares the segment for processing by adding the call and put strikes and
        merging with option prices and adding greeks"""

        entry_snapshot = self.snapshot_at_entry(segment_prices.iloc[0], num_strikes=30)
        logger.info(f"{self.underlying.name} delta backtest: built snapshot at entry")
        potential_strikes = np.unique(
            entry_snapshot[["call_strike", "put_strike"]].values
        ).tolist()
        if not all(self.strike_available(potential_strikes)):
            logger.info(
                f"Fetching missed strikes {potential_strikes} and some additional strikes for {segment_prices.iloc[0].name}"
            )
            additional_strikes = np.arange(
                min(potential_strikes) - 10 * self.underlying.base,
                max(potential_strikes)
                + 10 * self.underlying.base
                + self.underlying.base,
                self.underlying.base,
            ).tolist()
            self.fetch_missed_strikes(additional_strikes, segment_prices.iloc[0].name)
        self.check_option_prices_availability(entry_snapshot)

        entry_snapshot = self.merge_with_option_prices(entry_snapshot)
        logger.info(
            f"{self.underlying.name} delta backtest: merged snapshot at entry with option prices"
        )
        entry_snapshot = add_greeks_to_dataframe(
            entry_snapshot, r_col="r", use_one_iv=False
        )
        logger.info(
            f"{self.underlying.name} delta backtest: added greeks to snapshot at entry"
        )

        # Calculating strikes and ratios
        strikes = self.calculate_strikes_and_ratios(
            entry_snapshot, delta_range, target_delta
        )

        if not strikes:
            logger.info(
                f"{self.underlying.name} delta backtest: "
                f"no positions suitable for timestamp {segment_prices.iloc[0].name}. "
                f"Fast forwarding to next timestamp."
            )
            return False

        position_df = segment_prices.copy()
        # Adding strikes and ratios to the segment
        position_df["call_strike"] = [strikes["calls"][0]] * len(position_df)
        position_df["call_ratio"] = [strikes["calls"][1]] * len(position_df)
        position_df["put_strike"] = [strikes["puts"][0]] * len(position_df)
        position_df["put_ratio"] = [strikes["puts"][1]] * len(position_df)
        position_df = position_df.explode(
            ["call_strike", "call_ratio", "put_strike", "put_ratio"]
        )

        logger.info(
            f"{self.underlying.name} delta backtest: built position with strikes and ratios"
        )

        self.check_option_prices_availability(position_df)
        position_with_option_prices = self.merge_with_option_prices(position_df)
        position_with_greeks = add_greeks_to_dataframe(
            position_with_option_prices, r_col="r", use_one_iv=False
        )
        logger.info(f"{self.underlying.name} delta backtest: added greeks to positions")

        position_with_greeks = position_with_greeks.set_index("timestamp")
        logger.info(f"{self.underlying.name} delta backtest: streamlined positions")
        return position_with_greeks.groupby(position_with_greeks.index)

    def calculate_hedge_delta(
        self,
        timestamp: datetime,
        information: pd.Series,
        hedges: dict[OptionType, dict],
    ) -> float:
        """Uses the stored option prices to calculate the hedge delta at a given timestamp"""
        total_delta = 0
        for option_type in hedges.keys():
            logger.info(f"Calculating hedge delta for {option_type}")
            prefix = "call" if option_type == OptionType.CALL else "put"
            for strike in hedges[option_type].keys():
                logger.info(f"Calculating hedge delta for {strike}")
                price = (
                    self.option_prices.loc[timestamp]
                    .query(f"strike == {strike}")
                    .get(f"{prefix}_price")
                    .values[0]
                )
                iv = bs.implied_volatility(
                    price,
                    information.open,
                    strike,
                    information.time_to_expiry,
                    information.r,
                    option_type.value,
                )
                delta_points = bs.delta(
                    information.open,
                    strike,
                    information.time_to_expiry,
                    information.r,
                    iv,
                    option_type.value,
                )
                delta = delta_points * hedges[option_type][strike]
                total_delta += delta
                logger.info(
                    f"Calculated hedge delta for {strike} with price {price} and "
                    f"iv {iv} as {delta} using delta points {delta_points} and qty {hedges[option_type][strike]}. "
                    f"Total delta: {total_delta}"
                )
        return total_delta

    def calculate_mtm(
        self,
        timestamp: datetime,
        positions: pd.DataFrame,
        starting_qty: int,
        hedges: dict[OptionType, dict],
    ) -> float:
        mtm = 0
        for option_type in hedges.keys():
            prefix = "call" if option_type == OptionType.CALL else "put"
            for strike in hedges[option_type].keys():
                price = (
                    self.option_prices.loc[timestamp]
                    .query(f"strike == {strike}")
                    .get(f"{prefix}_price")
                    .values[0]
                )
                mtm += price * hedges[option_type][strike]

        og_call_mtm = (
            positions["call_ratio"].mul(positions["call_price"]).sum() * starting_qty
        )  # Weighted average of call prices multiplied by the quantity

        og_put_mtm = (
            positions["put_ratio"].mul(positions["put_price"]).sum() * starting_qty
        )  # Weighted average of put prices multiplied by the quantity

        mtm += og_call_mtm + og_put_mtm
        return mtm

    def process_segment(
        self,
        prepared_segment: pd.DataFrame,
        positions,  # This is a pd.DataFrameGroupBy object
        starting_qty: int,
        max_hedge_ratio: float,
        delta_threshold_pct: float,
        exit_time: tuple[int, int],
    ) -> pd.DataFrame:
        def make_appends(_neutralized_delta: float = np.nan, _mtm: float = np.nan):
            premium_received_history.append(total_premium_received)
            og_delta_history.append(main_net_delta)
            hedge_delta_history.append(hedge_delta)
            net_delta_history.append(total_delta)
            neutralized_delta_history.append(neutralized_delta)
            hedge_position_history.append(
                {k: dict(v.copy()) for k, v in hedges.items()}
            )
            mtm_history.append(mtm)

        entry_data = positions.get_group(positions.keys[0])
        max_hedge_qty = int(starting_qty * max_hedge_ratio)
        starting_qty *= -1  # Converting to negative because we are shorting

        main_position = {
            OptionType.CALL: {
                "Strikes": entry_data["call_strike"].values,
                "Deltas": entry_data["call_delta"].values,
                "Ratios": entry_data["call_ratio"].values,
            },
            OptionType.PUT: {
                "Strikes": entry_data["put_strike"].values,
                "Deltas": entry_data["put_delta"].values,
                "Ratios": entry_data["put_ratio"].values,
            },
        }

        logger.info(
            f"og_starting_qty {starting_qty}\n"
            f"max_hedge_qty: {max_hedge_qty}\nentry_data:\n{entry_data.filter(regex='ratio|delta')}"
        )

        og_call_premium_received = (
            entry_data["call_ratio"].mul(entry_data["call_price"]).sum() * starting_qty
        )  # Weighted average of call prices multiplied by the quantity

        og_put_premium_received = (
            entry_data["put_ratio"].mul(entry_data["put_price"]).sum() * starting_qty
        )  # Weighted average of put prices multiplied by the quantity

        total_premium_received = og_call_premium_received + og_put_premium_received

        logger.info(f"total_premium_received: {total_premium_received}")

        # Initializing the hedge positions
        hedges = {
            OptionType.CALL: defaultdict(lambda: 0),
            OptionType.PUT: defaultdict(lambda: 0),
        }

        delta_threshold = abs(delta_threshold_pct * starting_qty)

        # Lists to store PnL and net delta for each minute
        premium_received_history = []
        og_delta_history = []
        hedge_delta_history = []
        net_delta_history = []
        neutralized_delta_history = []
        hedge_position_history = []
        mtm_history = []

        # Iterate through the data minute by minute
        for i, row in prepared_segment.iterrows():
            neutralized_delta = np.nan
            mtm = np.nan
            logger.info(f"Processing {i}, segment length {len(prepared_segment)}")
            position_current_state = positions.get_group(i)

            # Exit the position if the time is equal to or greater than the exit time
            if i.time() >= time(*exit_time):
                mtm = self.calculate_mtm(
                    i, position_current_state, starting_qty, hedges
                )
                # Make the final appends before breaking
                make_appends(neutralized_delta, mtm)
                logger.info(f"Breaking at {i} because exit time reached")
                break

            main_net_delta = (
                position_current_state["call_ratio"]
                .mul(position_current_state["call_delta"])
                .sum()
                + position_current_state["put_ratio"]
                .mul(position_current_state["put_delta"])
                .sum()
            )

            logger.info(
                f"main_net_delta: {main_net_delta} "
                f"calculated from current ratios and deltas:\n{position_current_state.filter(regex='ratio|delta')}"
            )

            main_net_delta = main_net_delta * starting_qty
            logger.info(f"main_net_delta: {main_net_delta}")
            hedge_delta = self.calculate_hedge_delta(i, row, hedges)
            logger.info(f"hedge_delta: {hedge_delta}")
            total_delta = main_net_delta + hedge_delta

            logger.info(
                f"total_delta: {total_delta}, delta_threshold: {delta_threshold}"
            )

            if abs(total_delta) > delta_threshold:
                atm_info = self.rolling_atm_info.loc[i]

                total_premium_received = update_hedges(
                    hedges,
                    atm_info,
                    total_delta,
                    total_premium_received,
                    delta_threshold,
                )

                new_hedge_delta = self.calculate_hedge_delta(i, row, hedges)
                neutralized_delta = main_net_delta + new_hedge_delta
                total_hedge_qty_call = sum(hedges[OptionType.CALL].values())
                total_hedge_qty_put = sum(hedges[OptionType.PUT].values())

                # Exit the position if the deltas are too different or if the position is too large
                if total_hedge_qty_call < -max_hedge_qty or (
                    total_hedge_qty_put < -max_hedge_qty
                ):
                    mtm = self.calculate_mtm(
                        i, position_current_state, starting_qty, hedges
                    )

                    # Make the final appends before breaking
                    make_appends(neutralized_delta, mtm)
                    logger.info(
                        f"Breaking at {i} because max hedge qty {max_hedge_qty} reached"
                    )
                    break

            # Append histories
            make_appends(neutralized_delta, mtm)

        segment_result = pd.DataFrame(
            {
                "main_position": [main_position] * len(hedge_position_history),
                "hedge_positions": hedge_position_history,
                "main_position_delta": og_delta_history,
                "hedge_delta": hedge_delta_history,
                "net_delta": net_delta_history,
                "neutralized_delta": neutralized_delta_history,
                "premium": premium_received_history,
                "mtm": mtm_history,
            },
            index=prepared_segment[(prepared_segment.index <= i)].index,
        )
        return segment_result

    @staticmethod
    def process_result(
        segment: pd.DataFrame, segment_result: pd.DataFrame
    ) -> pd.DataFrame:
        processed_result = segment_result.merge(
            segment, left_index=True, right_index=True
        )
        return processed_result

    def reset_state(self):
        self.expiry = None
        self._option_prices = pd.DataFrame()
        self.unique_strikes = []
        return self

    def fetch_and_prepare_index_prices(self, from_date, to_date, only_expiry):
        index_prices = self.fetch_index_prices(self.underlying.name, from_date, to_date)
        index_prices.set_index("timestamp", inplace=True)
        if only_expiry:
            index_prices = index_prices[
                [
                    _date in self.underlying.expiry_dates.date
                    for _date in index_prices.index.date
                ]
            ]
        return index_prices

    def run_day(
        self,
        intraday_prices: pd.DataFrame,
        start_after: tuple[int, int] = (9, 15),
        scan_exit_time: tuple[int, int] = (15, 29),
        starting_exposure: int = 10000000,
        max_hedge_ratio: float = 0.2,
        delta_range: tuple[float, float] = (0.01, 0.25),
        target_delta: float = 0.15,
        delta_threshold_pct: float = 0.02,
    ) -> pd.DataFrame:
        intraday_prices = intraday_prices[
            (intraday_prices.index.time > time(*start_after))
        ].copy()

        # Determine the starting quantity
        starting_qty = int(starting_exposure / intraday_prices.iloc[0]["open"])

        logger.info(
            f"{self.underlying.name} delta backtest: Running backtest for day {intraday_prices.index[0].date()}"
        )
        expiry = self.determine_expiry(intraday_prices.iloc[0])
        if self.expiry is None or self.expiry != expiry:
            self.reset_state()
            self.expiry = expiry
            self.fetch_and_store_option_prices(
                intraday_prices.iloc[0], 30
            )  # Fetching 10 strikes each side

        # Adding helper columns to the intraday prices
        intraday_prices["expiry"] = self.expiry.strftime("%d%b%y").upper()
        intraday_prices["time_to_expiry"] = (
            self.expiry - intraday_prices.index
        ).total_seconds() / (60 * 60 * 24 * 365)
        scan_exit_time = (
            min(scan_exit_time, (14, 40))
            if intraday_prices["time_to_expiry"].iloc[0] < 0.0008
            else scan_exit_time
        )  # 14:40 if expiry is less than 1 day
        if intraday_prices.index[-1].time() < time(*scan_exit_time):
            logger.info(
                f"{self.underlying.name} delta backtest: "
                f"Skipping {intraday_prices.index[-1].date} as the last timestamp is before scan exit time"
            )
            return pd.DataFrame()
        self.store_atm_info(intraday_prices)
        moving_interest_rates = self.calculate_moving_interest_rate()
        self.add_greeks_to_rolling_atm_info()
        intraday_prices = intraday_prices.merge(
            moving_interest_rates, on="timestamp", how="left"
        )
        intraday_prices = intraday_prices.astype({"r": "float64"})
        intraday_prices.set_index("timestamp", inplace=True)

        current_segment = intraday_prices.copy()
        self.rolling_atm_info.set_index("timestamp", inplace=True)

        segment_results = []
        while not current_segment.empty and current_segment.index[0].time() < time(
            *scan_exit_time
        ):
            logger.info(
                f"{self.underlying.name} delta backtest: Running backtest for segment {current_segment.index[0]}"
            )
            # Strikes/prices/greeks are added here
            current_positions = self.prepare_positions(
                current_segment, delta_range, target_delta
            )
            if not current_positions:
                current_segment = intraday_prices[
                    intraday_prices.index > current_segment.index[0]
                ].copy()
                logger.info(
                    f"{self.underlying.name} delta backtest: Skipping {current_segment.index[0]}"
                )
                continue
            logger.info(
                f"{self.underlying.name} delta backtest: Prepared segment for {current_segment.index[0]}"
            )
            # The main processing function
            segment_result = self.process_segment(
                prepared_segment=current_segment,
                positions=current_positions,
                starting_qty=starting_qty,
                max_hedge_ratio=max_hedge_ratio,
                delta_threshold_pct=delta_threshold_pct,
                exit_time=scan_exit_time,
            )

            logger.info(
                f"{self.underlying.name} delta backtest: Processed segment for {current_segment.index[0]}"
            )
            segment_result = self.process_result(current_segment, segment_result)
            logger.info(
                f"{self.underlying.name} delta backtest: Processed result for {current_segment.index[0]}"
            )
            segment_results.append(segment_result)
            current_segment = intraday_prices[
                intraday_prices.index >= segment_result.index[-1]
            ].copy()
        return pd.concat(segment_results)

    def make_result_folder(self, folder_name: str = None):
        # Deciding the folder to store the results in
        directory = os.path.join(DeltaBackTest.RESULTS_FOLDER, self.underlying.name)
        if folder_name is None:
            if os.path.exists(directory):
                folder_number = len(os.listdir(directory)) + 1
            else:
                folder_number = 1
            folder_name = f"backtest_{folder_number}\\"
        else:
            folder_name = f"{folder_name}\\"
        directory = os.path.join(directory, folder_name)
        make_directory_if_needed(directory)
        return directory

    def run_backtest_subset(
        self,
        underlying: UnderlyingInfo,
        index_prices: pd.DataFrame,
        date_subset: list[datetime.date],
        result_folder: str,
        *args,
        **kwargs,
    ) -> None:
        """
        Runs the backtest for a subset of dates.
        """

        self.underlying = underlying
        self.expiry = None
        self._option_prices = pd.DataFrame()
        self.unique_strikes = []

        logger.info(f"Running backtest for {date_subset}")

        for date in date_subset:
            try:
                # Filter prices for the specific date
                prices = index_prices[index_prices.index.date == date]
                result = self.run_day(prices, *args, **kwargs)
                if not result.empty:
                    backtest_date = result.index[0].date()
                    filename = os.path.join(result_folder, f"{backtest_date}.csv")
                    result.to_csv(filename)
            except Exception as e:
                logger.error(f"Error while running backtest for {date}: {e}")

    def run_backtest_in_parallel(
        self,
        from_date: str | datetime,
        to_date: str | datetime = None,
        only_expiry: bool = False,
        folder_name: str = None,
        n_jobs: int = 5,
        *args,
        **kwargs,
    ):
        """
        Runs the backtest in parallel by splitting the index prices based on unique dates.
        """
        index_prices = self.fetch_and_prepare_index_prices(
            from_date, to_date, only_expiry
        )
        result_folder = self.make_result_folder(folder_name)

        # Split the unique dates into chunks for parallel processing
        split_dates = np.array_split(np.unique(index_prices.index.date), 5)

        # Add a check here that scans the result folder for existing results
        # and removes the dates that have already been processed
        processed_dates = [
            datetime.strptime(date.split(".")[0], "%Y-%m-%d").date()
            for date in os.listdir(result_folder)
        ]
        split_dates = [
            [
                pd.to_datetime(date).date()
                for date in chunk
                if date not in processed_dates
            ]
            for chunk in split_dates
        ]

        underlying = self.underlying

        # Prepare tasks for parallel execution
        tasks = [
            (
                lambda dc=date_chunk: self.run_backtest_subset(
                    underlying,
                    index_prices[pd.DatetimeIndex(index_prices.index.date).isin(dc)],
                    dc,
                    result_folder,
                    *args,
                    **kwargs,
                )
            )
            for date_chunk in split_dates
        ]

        logger.info(f"Running backtest for {len(tasks)} chunks")
        # Execute tasks in parallel
        results = execute_in_parallel(tasks, n_jobs=n_jobs)

        return results

    def run_backtest(
        self,
        from_date: str | datetime,
        to_date: str | datetime = None,
        only_expiry: bool = False,
        folder_name: str = None,
        *args,
        **kwargs,
    ):
        index_prices = self.fetch_and_prepare_index_prices(
            from_date, to_date, only_expiry
        )
        result_folder = self.make_result_folder(folder_name)
        for date, prices in index_prices.groupby(index_prices.index.date):
            try:
                result = self.run_day(prices, *args, **kwargs)
                if not result.empty:
                    backtest_date = result.index[0].date()
                    filename = os.path.join(result_folder, f"{backtest_date}.csv")
                    result.to_csv(filename)
            except Exception as e:
                logger.error(f"Error while running backtest for {date}: {e}")
                continue

    def consolidate_backtest(self, folder_name):
        path = os.path.join(
            DeltaBackTest.RESULTS_FOLDER, self.underlying.name, folder_name
        )
        full_df = pd.DataFrame()
        for day in os.listdir(path):
            day_df = pd.read_csv(os.path.join(path, day))
            full_df = pd.concat([full_df, day_df], ignore_index=True)
        full_df.set_index("timestamp", inplace=True)
        full_df.index = pd.to_datetime(full_df.index, dayfirst=True, format="mixed")
        return full_df


def update_hedges(
    hedges: dict[OptionType, dict],
    atm_info: pd.Series,
    total_delta: float,
    premium_received: float,
    delta_threshold: float,
) -> float:
    adjustment_type, adjustment_leg = (
        (OptionType.CALL, "call")
        if total_delta > delta_threshold
        else (OptionType.PUT, "put")
    )

    qty_to_sell = int((abs(total_delta) - 0) / abs(atm_info[f"{adjustment_leg}_delta"]))
    hedges[adjustment_type][atm_info[f"{adjustment_leg}_strike"]] -= qty_to_sell
    premium_received -= qty_to_sell * atm_info[f"{adjustment_leg}_price"]

    logger.info(
        f"Updating hedges for {atm_info.name}:\n"
        f"Adjustment: {adjustment_type}, "
        f"Strike: {atm_info[f'{adjustment_leg}_strike']}, "
        f"Qty: {qty_to_sell}, "
        f"Over all qty: {hedges[adjustment_type][atm_info[f'{adjustment_leg}_strike']]},"
        f"Delta: {atm_info[f'{adjustment_leg}_delta']}, "
        f"Price: {atm_info[f'{adjustment_leg}_price']}, "
        f"Premium received: {qty_to_sell * atm_info[f'{adjustment_leg}_price']}, "
        f"Over all premium received: {premium_received}, "
    )

    return premium_received


def summarize_results(df: pd.DataFrame) -> pd.DataFrame:
    # Identify duplicate timestamps, which signify exit points
    exits = df[~df.mtm.isna()].copy()  # Only consider rows with mtm

    # # Finding the last row of each day
    # final_exits = df.loc[
    #     df.groupby(df.index.date).apply(lambda x: x.iloc[-1].name).tolist()
    # ]

    # For each duplicate date, sum the 'premium' and 'mtm' to calculate profit
    exits["profit"] = abs(exits["premium"]) + exits["mtm"]

    return exits.sort_index()


def extreme_summary(
    summary: pd.DataFrame, exposure: float | None = None
) -> pd.DataFrame:
    summary = summary.copy()

    if exposure is None:
        exposure = 12000000

    summary["exposure"] = exposure
    summary["profit_percentage"] = (summary.profit / summary.exposure) * 100
    return summary.groupby(summary.index.date).profit_percentage.sum()


def compare_backtests(dbt: DeltaBackTest, backtests: list[str]) -> pd.DataFrame():
    """
    Compare the results of multiple backtests for the given underlying.

    Parameters:
        dbt (DeltaBackTest): An instance of DeltaBackTest.
        backtests (list[str]): A list of backtest names.

    Returns:
        DataFrame: A DataFrame containing the results of the backtests.
    """
    backtest_results = []
    for backtest in backtests:
        full_df = dbt.consolidate_backtest(backtest)
        summary = summarize_results(full_df)
        extreme_sum = extreme_summary(summary).to_frame()
        backtest_results.append(extreme_sum)
    return pd.concat(backtest_results, axis=1)
