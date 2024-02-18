from collections import defaultdict
from datetime import datetime, time
import json
import pandas as pd
import numpy as np
from volstreet.config import logger
from volstreet.utils import convert_to_serializable, round_to_nearest, find_strike
from volstreet.dealingroom import Index, calc_combined_premium
from volstreet.datamodule.eod_client import EODClient
from volstreet.datamodule.analysis import analyser


def get_recent_vol(df, periods=None, ignore_last=1):
    """Returns a dictionary of vol for each period in periods list
    :param df: Dataframe with 'abs_change' column
    :param periods: List of periods to calculate vol for
    :param ignore_last: Number of rows to ignore from the end
    :return: Dictionary of vol for each period in periods list
    """

    if periods is None:
        periods = [5]
    else:
        periods = [periods] if isinstance(periods, int) else periods

    if ignore_last == 0:
        df = df
    else:
        df = df.iloc[:-ignore_last]

    vol_dict = {}
    for period in periods:
        abs_change = df.tail(period).abs_change.mean()
        realized_vol = df.tail(period).realized_vol.mean()
        vol_dict[period] = (abs_change, realized_vol)
    return vol_dict


def resample_series(times, series, interval="1min"):
    """
    Resamples a time series of implied volatility (IV) into the given interval.

    Args:
        times (list): A list of datetime objects representing the timestamps.
        series (list): A list of IV values corresponding to the timestamps.
        interval (str): The resampling interval (default is '1min').

    Returns:
        list, list: The resampled IV series and resampled timestamps.
    """
    # Create a DataFrame with the time series data
    df = pd.DataFrame({"iv": series}, index=times)

    # Resample the data into the given interval
    resampled_df = df.resample(interval).last().ffill()

    # Return the resampled IV series and timestamps as lists
    return resampled_df["iv"].tolist(), resampled_df.index.tolist()


def reorganize_captured_data(data: dict, interval: str = "1min") -> dict:
    """
    Resamples the data into one-minute intervals and reorganizes it into the desired hierarchy:
    index -> strike -> expiry -> call/put/total.

    Args:
        data (dict): The original data structure.
        interval (str): The resampling interval (default is '1min').

    Returns:
        dict: The resampled and reorganized data.
    """

    def parse_timestamp(time_string, date=None):
        # Check if the time_string contains only the time (based on the absence of "-")
        if time_string.count(":") == 2 and time_string.count("-") == 0:
            assert (
                date is not None
            ), "Date must be provided if time_string contains only the time"
            # If a date portion is provided, combine it with the time
            return datetime.fromisoformat(date + " " + time_string)
        # If the time_string contains both date and time, parse it directly
        else:
            return datetime.fromisoformat(time_string)

    def handle_data_field(
        data_dict, field_name, timestamps, resample_interval, reorg_data_dict, stk, exp
    ):
        # Check if the field exists in the data
        if field_name in ["call_ltps", "put_ltps", "call_ivs", "put_ivs", "total_ivs"]:
            field_values = data_dict[field_name]
            field_values = [*map(lambda x: round_to_nearest(x, 3), field_values)]
            field_values, _ = resample_series(
                timestamps, field_values, resample_interval
            )
            reorg_data_dict[stk][exp][field_name] = field_values
        elif field_name == "times":
            _, resampled_ts = resample_series(timestamps, timestamps, resample_interval)
            reorg_data_dict[stk][exp]["times"] = resampled_ts
        else:
            pass

    reorganized_data = {}

    # Iterate through the indexes, expiries, and strikes
    for index_name, expiries in data.items():
        reorganized_data[index_name] = {}
        for expiry, strikes in expiries.items():
            for strike, strike_data in strikes.items():
                # Convert the strike to a string
                strike = str(strike)
                # Ensure the strike exists in the reorganized data
                if strike not in reorganized_data[index_name]:
                    reorganized_data[index_name][strike] = {}

                # Ensure the expiry exists in the reorganized data
                if expiry not in reorganized_data[index_name][strike]:
                    reorganized_data[index_name][strike][expiry] = {}

                # If the times are strings, parse them into datetime objects
                if isinstance(strike_data["times"][0], str):
                    # Extract the date portion from the last notified time if the times are only the time portion
                    if strike_data["times"][0].count("-") == 0:
                        date_portion = strike_data["last_notified_time"].split(" ")[0]
                        times = [
                            parse_timestamp(t, date_portion)
                            for t in strike_data["times"]
                        ]
                    else:
                        times = [parse_timestamp(t) for t in strike_data["times"]]

                # If the times are already datetime objects, use them directly
                elif isinstance(strike_data["times"][0], datetime):
                    times = strike_data["times"]

                # If the times are time objects, append the date portion to the times
                elif isinstance(strike_data["times"][0], time):
                    date_portion = strike_data["last_notified_time"].date()
                    times = [
                        datetime.combine(date_portion, t) for t in strike_data["times"]
                    ]

                else:
                    raise ValueError("Invalid type for times")

                data_fields = strike_data.keys()

                for field_name in data_fields:
                    handle_data_field(
                        strike_data,
                        field_name,
                        times,
                        interval,
                        reorganized_data[index_name],
                        strike,
                        expiry,
                    )

    return convert_to_serializable(reorganized_data)


def merge_reorganized_data(existing_data: dict, new_data: dict) -> dict:
    """
    Merges the new data into the existing data.

    Args:
        existing_data (dict): The existing data.
        new_data (dict): The new data.

    Returns:
        dict: The merged data.
    """

    if existing_data is None:
        existing_data = defaultdict(dict)

    # Iterate through the indexes, expiries, and strikes
    for index_name, strikes in new_data.items():
        for strike, strike_data in strikes.items():
            for expiry, expiry_data in strike_data.items():
                if index_name not in existing_data:
                    existing_data[index_name] = {}

                # Ensure the strike exists in the existing data
                if strike not in existing_data[index_name]:
                    existing_data[index_name][strike] = {}

                # Ensure the expiry exists in the existing data
                if expiry not in existing_data[index_name][strike]:
                    existing_data[index_name][strike][expiry] = {}
                data_fields = [
                    "call_ltps",
                    "put_ltps",
                    "call_ivs",
                    "put_ivs",
                    "total_ivs",
                    "times",
                ]
                for field_name in data_fields:
                    if field_name not in existing_data[index_name][strike][expiry]:
                        existing_data[index_name][strike][expiry][field_name] = []
                    if (
                        field_name not in expiry_data
                        or len(expiry_data[field_name]) == 0
                    ):
                        new_data = [np.nan] * len(expiry_data["times"])
                    else:
                        new_data = expiry_data[field_name]

                    existing_data[index_name][strike][expiry][field_name].extend(
                        new_data
                    )

    return existing_data


def store_captured_data(new_data: dict, filename: str):
    """
    Merges the new reorganized data with the existing data and stores it in the same JSON file.

    Args:
        new_data (dict): The new reorganized data.
        filename (str): The name of the file that contains existing data.
        If the file does not exist, it will be created as an empty dictionary.
    """

    try:
        with open(filename, "r") as f:
            existing_data = json.load(f)
    except FileNotFoundError:
        logger.info(
            f"File {filename} not found for storing captured price data. Creating a new file."
        )
        existing_data = {}
    except Exception as e:
        logger.error(f"Error while reading file to store captured data {filename}: {e}")
        raise e

    merged_data = merge_reorganized_data(existing_data, new_data)

    with open(filename, "w") as f:
        json.dump(merged_data, f)


def simulate_strike_premium_payoff(
    close: pd.Series,
    iv: pd.Series,
    time_to_expiry: pd.Series,
    strike_offset: float,
    base: float = 100,
    label: str = "",
    action="buy",
):
    if label:
        label = f"{label}_"

    action = action.lower()

    if action not in ["buy", "sell"]:
        raise ValueError("action must be either 'buy' or 'sell'")

    data = pd.DataFrame(
        {
            "close": close,
            "iv": iv,
            "time_to_expiry": time_to_expiry,
        }
    )

    data["call_strike"] = data["close"].apply(
        lambda x: find_strike(x * (1 + strike_offset), base)
    )
    data["put_strike"] = data["close"].apply(
        lambda x: find_strike(x * (1 - strike_offset), base)
    )
    data["outcome_spot"] = data["close"].shift(-1)
    data["initial_premium"] = data.apply(
        lambda row: calc_combined_premium(
            row.close,
            row.time_to_expiry,
            call_strike=row.call_strike,
            put_strike=row.put_strike,
            iv=row.iv / 100,
        ),
        axis=1,
    )
    data["outcome_premium"] = data.apply(
        lambda row: calc_combined_premium(
            row.outcome_spot,
            0,
            call_strike=row.call_strike,
            put_strike=row.put_strike,
            iv=row.iv / 100,
        ),
        axis=1,
    )
    data["payoff"] = (
        data["initial_premium"] - data["outcome_premium"]
        if action == "sell"
        else data["outcome_premium"] - data["initial_premium"]
    )
    data["payoff"] = data["payoff"].shift(1)
    data["payoff_pct"] = data["payoff"] / data["close"]
    data = data[
        [
            "call_strike",
            "put_strike",
            "initial_premium",
            "outcome_premium",
            "payoff",
            "payoff_pct",
        ]
    ]
    data.columns = [f"{label}{col}" for col in data.columns]
    return data


def get_index_vs_constituents_recent_vols(
    index_symbol,
    return_all=False,
    simulate_backtest=False,
    strike_offset=0,
    hedge_offset=0,
    stock_vix_adjustment=0.7,
    index_action="sell",
):
    """
    Get the recent volatility of the index and its constituents
    """
    if return_all is False:
        simulate_backtest = False

    index = Index(index_symbol)
    constituents, weights = index.get_constituents(cutoff_pct=90)
    weights = [w / sum(weights) for w in weights]

    dc = EODClient(api_key=__import__("os").environ["EOD_API_KEY"])

    index_data = dc.get_data(symbol=index_symbol)
    index_monthly_data = analyser(index_data, frequency="M-THU")
    index_monthly_data = index_monthly_data[["close", "abs_change"]]
    index_monthly_data.columns = ["index_close", "index_abs_change"]

    if simulate_backtest:
        if index_symbol == "BANKNIFTY":
            index_ivs = pd.read_csv(
                "data/banknifty_ivs.csv",
                parse_dates=True,
                index_col="date",
                dayfirst=True,
            )
            index_ivs.index = pd.to_datetime(index_ivs.index)
            index_ivs = index_ivs.resample("D").ffill()
            index_monthly_data = index_monthly_data.merge(
                index_ivs, left_index=True, right_index=True, how="left"
            )
            index_monthly_data["index_iv"] = index_monthly_data["close"].fillna(
                method="ffill"
            )
            index_monthly_data.drop(columns=["close"], inplace=True)
            index_monthly_data["iv_diff_from_mean"] = (
                index_monthly_data["index_iv"] / index_monthly_data["index_iv"].mean()
            )
            index_monthly_data["time_to_expiry"] = (
                index_monthly_data.index.to_series().diff().dt.days / 365
            )

            index_hedge_action = "buy" if index_action == "sell" else "sell"

            # The main strike
            simulated_data = simulate_strike_premium_payoff(
                index_monthly_data["index_close"],
                index_monthly_data["index_iv"],
                index_monthly_data["time_to_expiry"],
                strike_offset,
                100,
                label="index",
                action=index_action,
            )
            index_monthly_data = index_monthly_data.merge(
                simulated_data, left_index=True, right_index=True, how="left"
            )

            index_monthly_data["index_initial_premium_pct"] = (
                index_monthly_data["index_initial_premium"]
                / index_monthly_data["index_close"]
            )

            # The hedge strike
            simulated_data = simulate_strike_premium_payoff(
                index_monthly_data["index_close"],
                index_monthly_data["index_iv"],
                index_monthly_data["time_to_expiry"],
                hedge_offset,
                100,
                label="index_hedge",
                action=index_hedge_action,
            )

            index_monthly_data = index_monthly_data.merge(
                simulated_data, left_index=True, right_index=True, how="left"
            )

            index_monthly_data["index_hedge_initial_premium_pct"] = (
                index_monthly_data["index_hedge_initial_premium"]
                / index_monthly_data["index_close"]
            )

            index_monthly_data["index_bep_pct"] = (
                index_monthly_data["index_initial_premium_pct"]
                - index_monthly_data["index_hedge_initial_premium_pct"]
            )

        else:
            raise NotImplementedError

    constituent_dfs = []
    for i, constituent in enumerate(constituents):
        constituent_data = dc.get_data(symbol=constituent)
        constituent_monthly_data = analyser(constituent_data, frequency="M-THU")
        constituent_monthly_data = constituent_monthly_data[["close", "abs_change"]]
        constituent_monthly_data.columns = [
            f"{constituent}_close",
            f"{constituent}_abs_change",
        ]
        constituent_monthly_data[f"{constituent}_abs_change_weighted"] = (
            constituent_monthly_data[f"{constituent}_abs_change"] * weights[i]
        )

        if simulate_backtest:
            constituent_monthly_data[f"{constituent}_iv"] = index_monthly_data[
                "iv_diff_from_mean"
            ] * (
                (
                    constituent_monthly_data[f"{constituent}_abs_change"].mean()
                    - stock_vix_adjustment
                )
                * 4.4
            )  # the adjustment factor is to account for the spurious volatility on account of splits

            constituent_action = "buy" if index_action == "sell" else "sell"
            constituent_hedge_action = "sell" if constituent_action == "buy" else "sell"

            # The main strike
            simulated_data = simulate_strike_premium_payoff(
                constituent_monthly_data[f"{constituent}_close"],
                constituent_monthly_data[f"{constituent}_iv"],
                index_monthly_data["time_to_expiry"],
                strike_offset,
                5,
                label=constituent,
                action=constituent_action,
            )
            constituent_monthly_data = constituent_monthly_data.merge(
                simulated_data, left_index=True, right_index=True, how="left"
            )

            constituent_monthly_data[f"{constituent}_initial_premium_pct"] = (
                constituent_monthly_data[f"{constituent}_initial_premium"]
                / constituent_monthly_data[f"{constituent}_close"]
            )

            # The hedge strike
            simulated_data = simulate_strike_premium_payoff(
                constituent_monthly_data[f"{constituent}_close"],
                constituent_monthly_data[f"{constituent}_iv"],
                index_monthly_data["time_to_expiry"],
                hedge_offset,
                5,
                label=f"{constituent}_hedge",
                action=constituent_hedge_action,
            )
            constituent_monthly_data = constituent_monthly_data.merge(
                simulated_data, left_index=True, right_index=True, how="left"
            )

            constituent_monthly_data[f"{constituent}_hedge_initial_premium_pct"] = (
                constituent_monthly_data[f"{constituent}_hedge_initial_premium"]
                / constituent_monthly_data[f"{constituent}_close"]
            )

            constituent_monthly_data[f"{constituent}_bep_pct"] = (
                constituent_monthly_data[f"{constituent}_initial_premium_pct"]
                - constituent_monthly_data[f"{constituent}_hedge_initial_premium_pct"]
            )

            constituent_monthly_data[f"{constituent}_total_payoff"] = (
                constituent_monthly_data[f"{constituent}_payoff"]
                + constituent_monthly_data[f"{constituent}_hedge_payoff"]
            )
            constituent_monthly_data[f"{constituent}_total_payoff_pct"] = (
                constituent_monthly_data[f"{constituent}_total_payoff"]
                / constituent_monthly_data[f"{constituent}_close"]
            )
            constituent_monthly_data[f"{constituent}_total_payoff_pct_weighted"] = (
                constituent_monthly_data[f"{constituent}_total_payoff_pct"] * weights[i]
            )

        constituent_dfs.append(constituent_monthly_data)

    index_monthly_data = index_monthly_data.merge(
        pd.concat(constituent_dfs, axis=1),
        left_index=True,
        right_index=True,
        how="inner",
    )
    index_monthly_data = index_monthly_data.copy()
    index_monthly_data["sum_constituent_movement"] = index_monthly_data.filter(
        regex="abs_change_weighted"
    ).sum(axis=1)
    index_monthly_data["ratio_of_movements"] = (
        index_monthly_data["sum_constituent_movement"]
        / index_monthly_data["index_abs_change"]
    )

    if simulate_backtest:
        index_monthly_data["index_total_payoff"] = (
            index_monthly_data["index_payoff"]
            + index_monthly_data["index_hedge_payoff"]
        )
        index_monthly_data["index_total_payoff_pct"] = (
            index_monthly_data["index_total_payoff"] / index_monthly_data["index_close"]
        )
        index_monthly_data["sum_constituent_payoff_pct"] = index_monthly_data.filter(
            regex="total_payoff_pct_weighted"
        ).sum(axis=1)

        index_monthly_data["total_combined_payoff_pct"] = (
            index_monthly_data["index_total_payoff_pct"]
            + index_monthly_data["sum_constituent_payoff_pct"]
        )

    if return_all:
        return index_monthly_data
    else:
        summary_df = index_monthly_data[
            ["index_abs_change", "sum_constituent_movement", "ratio_of_movements"]
        ]
        summary_df["index_rolling"] = (
            summary_df["index_abs_change"].rolling(12, min_periods=1).mean()
        )
        summary_df["cons_rolling"] = (
            summary_df["sum_constituent_movement"].rolling(12, min_periods=1).mean()
        )
        summary_df["rolling_ratio"] = (
            summary_df["cons_rolling"] / summary_df["index_rolling"]
        )
        return summary_df
