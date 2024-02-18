import numpy as np
import pandas as pd
from collections import defaultdict
from datetime import time, timedelta
from time import sleep
from volstreet.config import logger
from volstreet.utils import (
    notifier,
    current_time,
    time_to_expiry,
    round_to_nearest,
    parse_symbol,
    find_strike,
    check_for_weekend,
)
from volstreet.angel_interface.interface import fetch_book, lookup_and_return
from volstreet.angel_interface.price_websocket import PriceWebsocket
from volstreet.trade_interface import (
    Option,
    Index,
)
from volstreet import blackscholes as bs


class OptionChains(defaultdict):
    """An object for having option chains for multiple expiries.
    Each expiry is a dictionary with integer default values"""

    def __init__(self):
        super().__init__(lambda: defaultdict(lambda: defaultdict(int)))
        self.underlying_price = None
        self.exp_strike_pairs = []


class OptionWatchlist(PriceWebsocket):
    def __init__(self, webhook_url=None, correlation_id="default"):
        super().from_active_session(
            webhook_url=webhook_url, correlation_id=correlation_id
        )
        self.iv_log = defaultdict(lambda: defaultdict(dict))
        self.index_option_chains_subscribed = []
        self.symbol_option_chains = {}

    def add_options(self, *underlyings, range_of_strikes=10, expiries=None, mode=1):
        for underlying in underlyings:
            if underlying.name not in self.symbol_option_chains:
                self.symbol_option_chains[underlying.name] = OptionChains()
                self.index_option_chains_subscribed.append(underlying.name)
        super().subscribed_to_options(
            *underlyings,
            range_of_strikes=range_of_strikes,
            expiries=expiries,
            mode=mode,
        )

    def update_option_chain(
        self,
        exit_time=(15, 30),
        process_price_iv_log=True,
        market_depth=True,
        calc_iv=True,
        stop_iv_calculation_hours=3,
        n_values=100,
    ):
        while current_time().time() < time(*exit_time):
            self.build_all_option_chains(
                market_depth=market_depth,
                process_price_iv_log=process_price_iv_log,
                calc_iv=calc_iv,
                stop_iv_calculation_hours=stop_iv_calculation_hours,
                n_values=n_values,
            )

    def build_option_chain(
        self,
        index: str,
        expiry: str,
        market_depth: bool = False,
        process_price_iv_log: bool = False,
        calc_iv: bool = False,
        n_values: int = 100,
        stop_iv_calculation_hours: int = 3,
    ):
        parsed_dict = self.parse_price_dict()
        instrument_info = parsed_dict[index]
        spot = instrument_info["ltp"]

        for symbol, info in parsed_dict.items():
            if symbol.startswith(index) and "CE" in symbol and expiry in symbol:
                strike = float(parse_symbol(symbol)[2])
                put_symbol = symbol.replace("CE", "PE")
                put_option = parsed_dict[put_symbol]
                call_price = info["ltp"]
                put_price = put_option["ltp"]

                self.symbol_option_chains[index][expiry][strike][
                    "call_price"
                ] = call_price
                self.symbol_option_chains[index][expiry][strike][
                    "put_price"
                ] = put_price
                self.symbol_option_chains[index].underlying_price = spot

                if calc_iv:
                    time_left_to_expiry = time_to_expiry(expiry)
                    if time_left_to_expiry < stop_iv_calculation_hours / (
                        24 * 365
                    ):  # If time to expiry is less than n hours stop calculating iv
                        if process_price_iv_log:
                            self.process_price_iv_log(
                                index,
                                strike,
                                expiry,
                                call_price,
                                put_price,
                                np.nan,
                                np.nan,
                                np.nan,
                                n_values,
                            )
                        continue
                    call_iv, put_iv, avg_iv = bs.calculate_strangle_iv(
                        call_price,
                        put_price,
                        spot,
                        strike=strike,
                        time_left=time_left_to_expiry,
                    )
                    self.symbol_option_chains[index][expiry][strike][
                        "call_iv"
                    ] = call_iv
                    self.symbol_option_chains[index][expiry][strike]["put_iv"] = put_iv
                    self.symbol_option_chains[index][expiry][strike]["avg_iv"] = avg_iv

                    if process_price_iv_log:
                        self.process_price_iv_log(
                            index,
                            strike,
                            expiry,
                            call_price,
                            put_price,
                            call_iv,
                            put_iv,
                            avg_iv,
                            n_values,
                        )

                if market_depth:
                    self.symbol_option_chains[index][expiry][strike][
                        "call_best_bid"
                    ] = info["best_bid"]
                    self.symbol_option_chains[index][expiry][strike][
                        "call_best_ask"
                    ] = info["best_ask"]
                    self.symbol_option_chains[index][expiry][strike][
                        "put_best_bid"
                    ] = put_option["best_bid"]
                    self.symbol_option_chains[index][expiry][strike][
                        "put_best_ask"
                    ] = put_option["best_ask"]
                    self.symbol_option_chains[index][expiry][strike][
                        "call_best_bid_qty"
                    ] = info["best_bid_qty"]
                    self.symbol_option_chains[index][expiry][strike][
                        "call_best_ask_qty"
                    ] = info["best_ask_qty"]
                    self.symbol_option_chains[index][expiry][strike][
                        "put_best_bid_qty"
                    ] = put_option["best_bid_qty"]
                    self.symbol_option_chains[index][expiry][strike][
                        "put_best_ask_qty"
                    ] = put_option["best_ask_qty"]

    def build_all_option_chains(
        self,
        indices: list[str] | str | None = None,
        expiries: list[list[str]] | list[str] | str | None = None,
        market_depth: bool = False,
        process_price_iv_log: bool = False,
        calc_iv: bool = False,
        n_values: int = 100,
        stop_iv_calculation_hours: int = 3,
    ):
        if indices is None:
            indices = self.index_option_chains_subscribed
        elif isinstance(indices, str):
            indices = [indices]
        else:
            indices = indices
        if expiries is None:
            expiries = [
                set([*zip(*self.symbol_option_chains[index].exp_strike_pairs)][0])
                for index in indices
            ]
        elif isinstance(expiries, str):
            expiries = [[expiries]]
        elif all([isinstance(expiry, str) for expiry in expiries]):
            expiries = [expiries]
        else:
            expiries = expiries

        for index, exps in zip(indices, expiries):
            for expiry in exps:
                self.build_option_chain(
                    index,
                    expiry,
                    market_depth,
                    process_price_iv_log,
                    calc_iv,
                    n_values,
                    stop_iv_calculation_hours,
                )

    def process_price_iv_log(
        self,
        index,
        strike,
        expiry,
        call_ltp,
        put_ltp,
        call_iv,
        put_iv,
        avg_iv,
        n_values,
    ):
        if strike not in self.iv_log[index][expiry]:
            self.iv_log[index][expiry][strike] = {
                "call_ltps": [],
                "put_ltps": [],
                "call_ivs": [],
                "put_ivs": [],
                "total_ivs": [],
                "times": [],
                "count": 0,
                "last_notified_time": current_time(),
            }
        self.iv_log[index][expiry][strike]["call_ltps"].append(
            round_to_nearest(call_ltp, 2)
        )
        self.iv_log[index][expiry][strike]["put_ltps"].append(
            round_to_nearest(put_ltp, 2)
        )
        self.iv_log[index][expiry][strike]["call_ivs"].append(
            round_to_nearest(call_iv, 3)
        )
        self.iv_log[index][expiry][strike]["put_ivs"].append(
            round_to_nearest(put_iv, 3)
        )
        self.iv_log[index][expiry][strike]["total_ivs"].append(
            round_to_nearest(avg_iv, 3)
        )
        self.iv_log[index][expiry][strike]["times"].append(current_time())
        self.iv_log[index][expiry][strike]["count"] += 1

        call_ivs, put_ivs, total_ivs = self.get_recent_ivs(
            index, expiry, strike, n_values
        )

        running_avg_call_iv = sum(call_ivs) / len(call_ivs) if call_ivs else None
        running_avg_put_iv = sum(put_ivs) / len(put_ivs) if put_ivs else None
        running_avg_total_iv = sum(total_ivs) / len(total_ivs) if total_ivs else None

        self.symbol_option_chains[index][expiry][strike].update(
            {
                "running_avg_call_iv": running_avg_call_iv,
                "running_avg_put_iv": running_avg_put_iv,
                "running_avg_total_iv": running_avg_total_iv,
            }
        )

    def get_recent_ivs(self, index, expiry, strike, n_values):
        call_ivs = self.iv_log[index][expiry][strike]["call_ivs"][-n_values:]
        put_ivs = self.iv_log[index][expiry][strike]["put_ivs"][-n_values:]
        total_ivs = self.iv_log[index][expiry][strike]["total_ivs"][-n_values:]
        call_ivs = [*filter(lambda x: x is not None, call_ivs)]
        put_ivs = [*filter(lambda x: x is not None, put_ivs)]
        total_ivs = [*filter(lambda x: x is not None, total_ivs)]
        return call_ivs, put_ivs, total_ivs


class SharedData:
    def __init__(self):
        self.position_data = None
        self.orderbook_data = None
        self.updated_time = None
        self.error_info = None
        self.force_stop = False

    def fetch_data(self):
        try:
            self.position_data = fetch_book("position")
            self.orderbook_data = fetch_book("orderbook")
            self.updated_time = current_time()
        except Exception as e:
            self.position_data = None
            self.orderbook_data = None
            self.error_info = e

    def update_data(self, sleep_time=5, exit_time=(15, 30)):
        while current_time().time() < time(*exit_time) and not self.force_stop:
            self.fetch_data()
            sleep(sleep_time)


class SyntheticArbSystem:
    def __init__(self, symbol_option_chains):
        self.symbol_option_chains = symbol_option_chains

    def find_arbitrage_opportunities(
        self,
        index: str,
        expiry: str,
        qty_in_lots: int,
        exit_time=(15, 28),
        threshold=3,  # in points
    ):
        def get_single_index_single_expiry_data(_index, _expiry):
            option_chain = self.symbol_option_chains[_index][_expiry]
            _strikes = [_s for _s in option_chain]
            _call_prices = [option_chain[_s]["call_price"] for _s in _strikes]
            _put_prices = [option_chain[_s]["put_price"] for _s in _strikes]
            _call_bids = [option_chain[_s]["call_best_bid"] for _s in _strikes]
            _call_asks = [option_chain[_s]["call_best_ask"] for _s in _strikes]
            _put_bids = [option_chain[_s]["put_best_bid"] for _s in _strikes]
            _put_asks = [option_chain[_s]["put_best_ask"] for _s in _strikes]
            _call_bid_qty = [option_chain[_s]["call_best_bid_qty"] for _s in _strikes]
            _call_ask_qty = [option_chain[_s]["call_best_ask_qty"] for _s in _strikes]
            _put_bid_qty = [option_chain[_s]["put_best_bid_qty"] for _s in _strikes]
            _put_ask_qty = [option_chain[_s]["put_best_ask_qty"] for _s in _strikes]

            return (
                np.array(_strikes),
                np.array(_call_prices),
                np.array(_put_prices),
                np.array(_call_bids),
                np.array(_call_asks),
                np.array(_put_bids),
                np.array(_put_asks),
                np.array(_call_bid_qty),
                np.array(_call_ask_qty),
                np.array(_put_bid_qty),
                np.array(_put_ask_qty),
            )

        def return_both_side_synthetic_prices(
            _strikes, _call_asks, _put_bids, _call_bids, _put_asks
        ):
            return (_strikes + _call_asks - _put_bids), (
                _strikes + _call_bids - _put_asks
            )

        (
            strikes,
            call_prices,
            put_prices,
            call_bids,
            call_asks,
            put_bids,
            put_asks,
            call_bid_qty,
            call_ask_qty,
            put_bid_qty,
            put_ask_qty,
        ) = get_single_index_single_expiry_data(index, expiry)
        synthetic_buy_prices, synthetic_sell_prices = return_both_side_synthetic_prices(
            strikes, call_asks, put_bids, call_bids, put_asks
        )
        min_price_index = np.argmin(synthetic_buy_prices)
        max_price_index = np.argmax(synthetic_sell_prices)
        min_price = synthetic_buy_prices[min_price_index]
        max_price = synthetic_sell_prices[max_price_index]

        last_print_time = current_time()
        while current_time().time() < time(*exit_time):
            if current_time() > last_print_time + timedelta(seconds=5):
                print(
                    f"{current_time()} - {index} - {expiry}:\n"
                    f"Minimum price: {min_price} at strike: {strikes[min_price_index]} "
                    f"Call Ask: {call_asks[min_price_index]} Put Bid: {put_bids[min_price_index]}\n"
                    f"Maximum price: {max_price} at strike: {strikes[max_price_index]} "
                    f"Call Bid: {call_bids[max_price_index]} Put Ask: {put_asks[max_price_index]}\n"
                    f"Price difference: {max_price - min_price}\n"
                )
                last_print_time = current_time()

            if max_price - min_price > threshold:
                print(
                    f"**********Trade Identified at {current_time()} on strike: Min {strikes[min_price_index]} "
                    f"and Max {strikes[max_price_index]}**********\n"
                    f"Minimum price: {min_price} at strike: {strikes[min_price_index]} "
                    f"Call Ask: {call_asks[min_price_index]} Put Bid: {put_bids[min_price_index]}\n"
                    f"Maximum price: {max_price} at strike: {strikes[max_price_index]} "
                    f"Call Bid: {call_bids[max_price_index]} Put Ask: {put_asks[max_price_index]}\n"
                    f"Price difference: {max_price - min_price}\n"
                )
                min_strike = strikes[min_price_index]
                max_strike = strikes[max_price_index]

                self.execute_synthetic_trade(
                    index,
                    expiry,
                    qty_in_lots,
                    min_strike,
                    max_strike,
                )

            for i, strike in enumerate(strikes):
                call_prices[i] = self.symbol_option_chains[index][expiry][strike][
                    "call_price"
                ]
                put_prices[i] = self.symbol_option_chains[index][expiry][strike][
                    "put_price"
                ]
                call_bids[i] = self.symbol_option_chains[index][expiry][strike][
                    "call_best_bid"
                ]
                call_asks[i] = self.symbol_option_chains[index][expiry][strike][
                    "call_best_ask"
                ]
                put_bids[i] = self.symbol_option_chains[index][expiry][strike][
                    "put_best_bid"
                ]
                put_asks[i] = self.symbol_option_chains[index][expiry][strike][
                    "put_best_ask"
                ]
                call_bid_qty[i] = self.symbol_option_chains[index][expiry][strike][
                    "call_best_bid_qty"
                ]
                call_ask_qty[i] = self.symbol_option_chains[index][expiry][strike][
                    "call_best_ask_qty"
                ]
                put_bid_qty[i] = self.symbol_option_chains[index][expiry][strike][
                    "put_best_bid_qty"
                ]
                put_ask_qty[i] = self.symbol_option_chains[index][expiry][strike][
                    "put_best_ask_qty"
                ]
            (
                synthetic_buy_prices,
                synthetic_sell_prices,
            ) = return_both_side_synthetic_prices(
                strikes, call_asks, put_bids, call_bids, put_asks
            )
            min_price_index = np.argmin(synthetic_buy_prices)
            max_price_index = np.argmax(synthetic_sell_prices)
            min_price = synthetic_buy_prices[min_price_index]
            max_price = synthetic_sell_prices[max_price_index]

    @staticmethod
    def execute_synthetic_trade(
        index,
        expiry,
        qty_in_lots,
        buy_strike,
        sell_strike,
    ):
        ids_call_buy, ids_put_sell = place_synthetic_fut_order(
            index, buy_strike, expiry, "BUY", qty_in_lots, "MARKET"
        )
        ids_call_sell, ids_put_buy = place_synthetic_fut_order(
            index, sell_strike, expiry, "SELL", qty_in_lots, "MARKET"
        )
        ids = np.concatenate((ids_call_buy, ids_put_sell, ids_call_sell, ids_put_buy))

        sleep(1)
        statuses = lookup_and_return("orderbook", "orderid", ids, "status")

        if any(statuses == "rejected"):
            logger.error(
                f"Order rejected for {index} {expiry} {qty_in_lots} Buy {buy_strike} Sell {sell_strike}"
            )


class IvArbitrageScanner:
    def __init__(self, symbol_option_chains, iv_log):
        self.symbol_option_chains = symbol_option_chains
        self.iv_log = iv_log
        self.trade_log = []

    def scan_for_iv_arbitrage(
        self, iv_hurdle=1.5, exit_time=(15, 25), notification_url=None
    ):
        while current_time().time() < time(*exit_time):
            for index in self.symbol_option_chains:
                spot = self.symbol_option_chains[index].underlying_price
                for expiry in self.symbol_option_chains[index]:
                    for strike in self.symbol_option_chains[index][expiry]:
                        option_to_check = "avg"

                        # Check for IV spike
                        if spot < strike + 100:
                            option_to_check = "call"

                        if spot > strike - 100:
                            option_to_check = "put"

                        try:
                            opt_iv = self.symbol_option_chains[index][expiry][strike][
                                f"{option_to_check}_iv"
                            ]
                            running_avg_opt_iv = self.symbol_option_chains[index][
                                expiry
                            ][strike][f"running_avg_{option_to_check}_iv"]
                        except KeyError as e:
                            print(f"KeyError {e} for {index} {expiry} {strike}")
                            raise e

                        self.check_iv_spike(
                            opt_iv,
                            running_avg_opt_iv,
                            option_to_check.capitalize(),
                            index,
                            strike,
                            expiry,
                            iv_hurdle,
                            notification_url,
                        )

    def check_iv_spike(
        self,
        iv,
        running_avg_iv,
        opt_type,
        underlying,
        strike,
        expiry,
        iv_hurdle,
        notification_url,
    ):
        if (
            opt_type == "Avg"
            or iv is None
            or running_avg_iv is None
            or np.isnan(iv)
            or np.isnan(running_avg_iv)
        ):
            return

        iv_hurdle = 1 + iv_hurdle
        upper_iv_threshold = running_avg_iv * iv_hurdle
        lower_iv_threshold = running_avg_iv / iv_hurdle

        # print(
        #    f"Checking {opt_type} IV for {underlying} {strike} {expiry}\nIV: {iv}\n"
        #    f"Running Average: {running_avg_iv}\nUpper Threshold: {upper_iv_threshold}\n"
        #    f"Lower Threshold: {lower_iv_threshold}"
        # )

        if iv and (iv > upper_iv_threshold or iv < lower_iv_threshold):
            # Execute trade
            # signal = "BUY" if iv > upper_iv_threshold else "SELL"
            # self.execute_iv_arbitrage_trade(
            #     signal, underlying, strike, expiry, opt_type
            # )

            # Notify
            if self.iv_log[underlying][expiry][strike][
                "last_notified_time"
            ] < current_time() - timedelta(minutes=5):
                notifier(
                    f"{opt_type} IV for {underlying} {strike} {expiry} different from average.\nIV: {iv}\n"
                    f"Running Average: {running_avg_iv}",
                    notification_url,
                    "INFO",
                )
                self.iv_log[underlying][expiry][strike][
                    "last_notified_time"
                ] = current_time()

    def execute_iv_arbitrage_trade(
        self, signal, underlying, strike, expiry, option_type
    ):
        qty_in_lots = 1
        option_to_trade = Option(strike, option_type, underlying, expiry)
        order_ids = option_to_trade.place_order(signal, qty_in_lots, "MARKET")
        self.trade_log.append(
            {
                "traded_option": option_to_trade,
                "order_ids": order_ids,
                "signal": signal,
                "qty": qty_in_lots,
                "order_type": "MARKET",
                "time": current_time(),
            }
        )


def fetch_orderbook_if_needed(
    data_class: SharedData = None, refresh_needed: bool = False
):
    if data_class is None:
        return fetch_book("orderbook")
    if refresh_needed:
        data_class.fetch_data()
    if (
        current_time() - data_class.updated_time < timedelta(seconds=15)
        and data_class.orderbook_data is not None
    ):
        return data_class.orderbook_data
    return fetch_book("orderbook")


def get_strangle_indices_to_trade(
    *indices: Index, safe_indices: list[str] | None = None, only_expiry: bool = False
) -> list[Index] | list[None]:
    if safe_indices is None:
        safe_indices = ["NIFTY", "BANKNIFTY"]

    times_to_expiries = [
        time_to_expiry(index.current_expiry, effective_time=True, in_days=True)
        for index in indices
    ]

    # Check if any index has less than 1 day to expiry
    indices_less_than_1_day = [
        index
        for index, time_left_to_expiry in zip(indices, times_to_expiries)
        if time_left_to_expiry < 1
    ]

    if indices_less_than_1_day or only_expiry:
        return indices_less_than_1_day

    # If no index has less than 1 day to expiry
    min_expiry_time = min(times_to_expiries)
    indices_with_closest_expiries = [
        index
        for index, time_left_to_expiry in zip(indices, times_to_expiries)
        if time_left_to_expiry == min_expiry_time
    ]
    weekend_in_range = check_for_weekend(
        indices_with_closest_expiries[0].current_expiry
    )

    if weekend_in_range:
        # Checking if the closest indices are safe indices
        safe_and_close = [
            index
            for index in indices_with_closest_expiries
            if index.name in safe_indices
        ]
        if (
            safe_and_close
        ):  # If the indices with the closest expiry are safe indices then return the closest indices
            return safe_and_close
        else:  # If the indices with the closest expiry are not safe indices then return safe indices
            return [index for index in indices if index.name in safe_indices]

    return indices_with_closest_expiries


def calc_combined_premium(
    spot,
    time_left,
    strike=None,
    call_strike=None,
    put_strike=None,
    iv=None,
    call_iv=None,
    put_iv=None,
):
    call_strike = call_strike if call_strike is not None else strike
    put_strike = put_strike if put_strike is not None else strike

    call_iv = call_iv if call_iv is not None else iv
    put_iv = put_iv if put_iv is not None else iv
    if time_left > 0:
        call_price = bs.call(spot, call_strike, time_left, 0.05, call_iv)
        put_price = bs.put(spot, put_strike, time_left, 0.05, put_iv)
        return call_price + put_price
    else:
        call_payoff = max(0, spot - call_strike)
        put_payoff = max(0, put_strike - spot)
        return call_payoff + put_payoff


def convert_option_chains_to_df(option_chains, return_all=False, for_surface=False):
    def add_columns_for_surface(data_frame):
        data_frame = data_frame.copy()
        data_frame["atm_strike"] = data_frame.apply(
            lambda row: find_strike(row.spot, 50)
            if row.symbol == "NIFTY"
            else find_strike(row.spot, 100),
            axis=1,
        )
        data_frame["strike_iv"] = np.where(
            data_frame.strike > data_frame.atm_strike,
            data_frame.call_iv,
            np.where(
                data_frame.strike < data_frame.atm_strike,
                data_frame.put_iv,
                data_frame.avg_iv,
            ),
        )
        data_frame["atm_iv"] = data_frame.apply(
            lambda row: data_frame[
                (data_frame.strike == row.atm_strike)
                & (data_frame.expiry == row.expiry)
            ].strike_iv.values[0],
            axis=1,
        )
        data_frame.sort_values(["symbol", "expiry", "strike"], inplace=True)
        data_frame["distance"] = data_frame["strike"] / data_frame["spot"] - 1
        data_frame["iv_multiple"] = data_frame["strike_iv"] / data_frame["atm_iv"]
        data_frame["distance_squared"] = data_frame["distance"] ** 2

        return data_frame

    symbol_dfs = []
    for symbol in option_chains:
        spot_price = option_chains[symbol].underlying_price
        expiry_dfs = []
        for expiry in option_chains[symbol]:
            df = pd.DataFrame(option_chains[symbol][expiry]).T
            df.index = df.index.set_names("strike")
            df = df.reset_index()
            df["spot"] = spot_price
            df["expiry"] = expiry
            df["symbol"] = symbol
            df["time_to_expiry"] = time_to_expiry(expiry)
            expiry_dfs.append(df)
        symbol_oc = pd.concat(expiry_dfs)
        if for_surface:
            symbol_oc = add_columns_for_surface(symbol_oc)
        symbol_dfs.append(symbol_oc)

    if return_all:
        return pd.concat(symbol_dfs)
    else:
        return symbol_dfs


def place_synthetic_fut_order(*args, **kwargs):
    logger.warning(
        f"place_synthetic_fut_order is deprecated. Use place_option_order_and_notify instead.{args}{kwargs}"
    )
    raise NotImplementedError
