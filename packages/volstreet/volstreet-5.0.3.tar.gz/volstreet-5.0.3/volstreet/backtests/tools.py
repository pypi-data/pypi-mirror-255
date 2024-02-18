import numpy as np
import pandas as pd
from datetime import datetime, time


def decode_trend_dynamics(trend_dataframe: pd.DataFrame) -> dict:
    def study_trade_data(series: pd.Series) -> dict:
        """
        This function studies the trade data from a series containing dictionaries
        and returns a dictionary with the following keys:
        Total stop-loss cost - Total pct points lost in stop-losses
        Total positive trend captured - Total pct points gained in positive trends
        Total negative trend captured - Total pct points lost in negative trends
        """

        # Initialize the dictionary
        trade_data_analysis: dict = {
            "total_entries": 0,
            "single_entry_successes": 0,
            "total_stop_loss_count": 0,
            "total_stop_loss_cost": 0,
            "total_positive_trend_captured": 0,
            "total_negative_trend_captured": 0,
        }

        # Iterate through the series and update the dictionary
        for day in series:
            max_entries = len(day) - 1
            if max_entries == 0:
                continue
            for entry in range(1, max_entries + 1):
                entry_data = day[f"entry_{entry}"]
                if isinstance(entry_data["stop_loss_time"], pd.Timestamp):
                    trade_data_analysis["total_stop_loss_cost"] += entry_data["returns"]
                    trade_data_analysis["total_stop_loss_count"] += 1
                else:
                    if entry_data["returns"] > 0:
                        trade_data_analysis[
                            "total_positive_trend_captured"
                        ] += entry_data["returns"]
                    else:
                        trade_data_analysis[
                            "total_negative_trend_captured"
                        ] += entry_data["returns"]
                trade_data_analysis["total_entries"] += 1
            if max_entries == 1:
                trade_data_analysis["single_entry_successes"] += 1

        return trade_data_analysis

    trade_analysis: dict = study_trade_data(trend_dataframe.trade_data)
    total_trend: float = trend_dataframe.open_to_close_trend_abs.sum()
    total_returns_check: float = trend_dataframe.total_returns.sum()
    prediction_accuracy: float = trend_dataframe.rolling_prediction_accuracy[-1]

    trade_analysis["total_trend"] = total_trend
    trade_analysis["total_returns_check"] = total_returns_check
    trade_analysis["single_entry_success_pct"] = (
        trade_analysis["single_entry_successes"] / trade_analysis["total_entries"]
    )
    trade_analysis["prediction_accuracy"] = prediction_accuracy
    trade_analysis["avg_entries_per_day"] = trade_analysis["total_entries"] / len(
        trend_dataframe
    )

    return trade_analysis


def nav_drawdown_analyser(
    df,
    column_to_convert="profit",
    base_price_col="close",
    nav_start=100,
    profit_in_pct=False,
):
    """Supply an analysed dataframe with a column that has the profit/loss in percentage or absolute value.
    Params:
    df: Dataframe with the column to be converted to NAV
    column_to_convert: Column name to be converted to NAV (default: 'profit')
    nav_start: Starting NAV (default: 100)
    profit_in_pct: If the column is in percentage or absolute value (default: False)
    """

    if column_to_convert not in df.columns:
        raise ValueError(f"No column '{column_to_convert}' found in DataFrame.")

    df = df.copy(deep=True)

    if not profit_in_pct:
        df["profit_pct"] = (df[column_to_convert] / df[base_price_col]) * 100
    else:
        df["profit_pct"] = df[column_to_convert]

    df["strat_nav"] = ((df["profit_pct"] + 100) / 100).cumprod() * nav_start
    df["cum_max"] = df["strat_nav"].cummax()
    df["drawdown"] = ((df["strat_nav"] / df["cum_max"]) - 1) * 100

    df["rolling_cagr"] = df.apply(
        lambda row: np.nan
        if (df.index[-1] - row.name).days
        < 30  # Hardcoded 30 days is the minimum period for CAGR
        else (
            (df["strat_nav"].iloc[-1] / row["strat_nav"])
            ** (1 / ((df.index[-1] - row.name).days / 365))
            - 1
        )
        * 100,
        axis=1,
    )

    drawdown_checker = df["drawdown"].ne(0).astype(int)
    change_in_trend = drawdown_checker.ne(drawdown_checker.shift(1))

    start_of_drawdown = change_in_trend & (drawdown_checker == 1)
    df["drawdown_id"] = start_of_drawdown.cumsum()
    df["drawdown_id"] = df["drawdown_id"].where(drawdown_checker == 1, np.nan)

    df = df.drop(["profit_pct", "cum_max"], axis=1)
    df.index = pd.to_datetime(df.index)

    return df


def prepare_index_prices_for_backtest(
    index_prices, start_after=(9, 15), end_before=(15, 30)
) -> pd.DataFrame:
    unavailable_dates = [
        datetime(2016, 10, 30).date(),
        datetime(2019, 10, 27).date(),
        datetime(2020, 11, 14).date(),
    ]

    index_prices = index_prices.copy()

    index_prices = index_prices[
        (index_prices["timestamp"].dt.time > time(*start_after))
        & (index_prices["timestamp"].dt.time < time(*end_before))
    ]

    index_prices.drop(
        index_prices[index_prices["timestamp"].dt.date.isin(unavailable_dates)].index,
        inplace=True,
    )

    return index_prices


def filter_duplicate_trades(
    df: pd.DataFrame, trigger_col: str = "trigger_time", exit_col: str = "exit_time"
) -> pd.DataFrame:
    """Supply a dataframe with trades and columns for trigger and exit times."""

    # Initialize an empty DataFrame to store the filtered trades
    filtered_rows = []

    # Initialize a variable to store the latest exit time of the trades included
    latest_exit_time = pd.Timestamp.min

    # Loop through each row in the DataFrame
    for idx, row in df.iterrows():
        # If this is the first trade or its trigger_time is later than the latest_exit_time, include it
        if row[trigger_col] > latest_exit_time:
            filtered_rows.append(row)
            latest_exit_time = row[exit_col]

    # Show the first few rows of the filtered DataFrame
    filtered_df = pd.DataFrame(filtered_rows)
    filtered_df.index = pd.to_datetime(filtered_df.index)

    return filtered_df
