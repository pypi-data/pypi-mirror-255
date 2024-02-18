from datetime import timedelta
import numpy as np
import pandas as pd
from dateutil.relativedelta import MO, TU, WE, TH, FR, relativedelta


def analyser(df, frequency=None, date_filter=None, _print=False):
    name = df.name

    # Saving market days for later adjustment
    market_days = df.index
    if date_filter is None:
        pass
    else:
        dates = date_filter.split("to")
        if len(dates) > 1:
            df = df.loc[dates[0] : dates[1]]
        else:
            df = df.loc[dates[0]]

    frequency = frequency.upper() if frequency is not None else None

    if frequency is None or frequency.startswith("D") or frequency == "B":
        custom_frequency = "B"
        multiplier = 24
        df = df.resample("B").ffill()

    elif frequency.startswith("W") or frequency.startswith("M"):
        custom_frequency = frequency
        if frequency.startswith("W"):
            multiplier = 9.09
            df = df.resample(frequency).ffill()
        elif frequency.startswith("M"):
            multiplier = 4.4
            if len(frequency) == 1:
                df = df.resample("M").ffill()
            else:
                weekday_module_dict = {
                    "MON": MO,
                    "TUE": TU,
                    "WED": WE,
                    "THU": TH,
                    "FRI": FR,
                }
                frequency = frequency.lstrip("M-")
                df = df.resample(f"W-{frequency.upper()}").ffill()
                df = df.resample("M").ffill()
                df.index = df.index.date + relativedelta(
                    weekday=weekday_module_dict[frequency.upper()](-1)
                )
                df.index = pd.Series(pd.to_datetime(df.index), name="date")
        else:
            raise ValueError("Frequency not supported")
    else:
        raise ValueError("Frequency not supported")

    df.loc[:, "change"] = df.close.pct_change() * 100
    df.loc[:, "abs_change"] = abs(df.change)
    df.loc[:, "realized_vol"] = df.abs_change * multiplier

    if frequency in ["D-MON", "D-TUE", "D-WED", "D-THU", "D-FRI"]:
        day_of_week = frequency.split("-")[1]
        df = df[df.index.day_name().str.upper().str.contains(day_of_week)]

    if _print:
        print(
            "Vol for period: {:0.2f}%, IV: {:0.2f}%".format(
                df.abs_change.mean(), df.abs_change.mean() * multiplier
            )
        )
    else:
        pass

    # Shifting simulated market days to market days
    while not all(df.index.isin(market_days)):
        df.index = pd.Index(
            np.where(
                ~df.index.isin(market_days), df.index - timedelta(days=1), df.index
            )
        )

    # Dropping duplicated index values that resulted from
    # resampling and shifting of simulated market days to market days
    df = df[~df.index.duplicated(keep="first")]

    # Setting the index name, custom frequency and name
    df.index.name = "date"
    df.custom_frequency = custom_frequency.upper()
    df.name = name
    return df


def ratio_analysis(
    x_df: pd.DataFrame,
    y_df: pd.DataFrame,
    periods_to_avg: int = None,
    return_summary=True,
    add_rolling: bool | int = False,
):
    if periods_to_avg is None:
        periods_to_avg = len(x_df)

    x_close = x_df.iloc[-periods_to_avg:].close
    x_array = x_df.iloc[-periods_to_avg:].abs_change
    x_avg = x_array.mean()

    y_close = y_df.iloc[-periods_to_avg:].close
    y_array = y_df.iloc[-periods_to_avg:].abs_change
    y_avg = y_array.mean()

    avg_ratio = x_avg / y_avg
    ratio_array = x_df.abs_change / y_df.abs_change
    ratio_array = ratio_array[-periods_to_avg:]

    labels = [x_df.name, y_df.name]

    ratio_summary = pd.DataFrame(
        {
            labels[0]: x_close,
            f"{labels[0]} Change": x_array,
            labels[1]: y_close,
            f"{labels[1]} Change": y_array,
            "Ratio": ratio_array,
        }
    )
    # print(f'\n{periods_to_avg} Period Average = {avg_ratio}\n\n')
    if return_summary:
        ratio_summary.loc["Summary"] = ratio_summary.mean()
        ratio_summary.loc["Summary", "Ratio"] = avg_ratio

    if add_rolling:
        rolling_x_avg = x_array.rolling(add_rolling, min_periods=1).mean()
        rolling_y_avg = y_array.rolling(add_rolling, min_periods=1).mean()
        rolling_ratio = rolling_x_avg / rolling_y_avg
        ratio_summary[f"Rolling {add_rolling} Ratio"] = rolling_ratio

    return ratio_summary


def downside_deviation(series, threshold=None):
    """
    Compute the downside deviation of series of returns.

    Parameters:
    - series: A pandas Series with returns.
    - threshold: The minimum acceptable return. Default is the mean return.

    Returns:
    - The downside deviation.
    """
    if threshold is None:
        threshold = series.mean()

    downside_diff = series.apply(lambda x: min(0, x - threshold))

    return (downside_diff**2).mean() ** 0.5


def calculate_directional_index(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """Supply a dataframe with high, low and close columns and it will create the ADX indicator"""

    # Calculate True Range
    df["high_low"] = df["high"] - df["low"]
    df["high_close"] = np.abs(df["high"] - df["close"].shift(1))
    df["low_close"] = np.abs(df["low"] - df["close"].shift(1))

    df["TR"] = df[["high_low", "high_close", "low_close"]].max(axis=1)

    # Calculate +DM and -DM
    delta_high = df["high"].diff()
    delta_low = df["low"].diff()

    # Corrected conditions for +DM and -DM
    df["+DM"] = np.where(
        (delta_high > 0)
        & (
            delta_high > -delta_low
        ),  # Ensuring that higher high is greater than lower low
        delta_high,
        0,
    )
    df["-DM"] = np.where(
        (delta_low < 0)
        & (
            delta_low < -delta_high
        ),  # Ensuring that lower low is greater than higher high
        np.abs(delta_low),
        0,
    )

    # Smoothed Averages
    df["Smoothed_TR"] = (
        df["TR"]
        .rolling(window=period)
        .apply(lambda x: x.sum() if x.isna().sum() == 0 else np.nan)
    )
    df["Smoothed_+DM"] = (
        df["+DM"]
        .rolling(window=period)
        .apply(lambda x: x.sum() if x.isna().sum() == 0 else np.nan)
    )
    df["Smoothed_-DM"] = (
        df["-DM"]
        .rolling(window=period)
        .apply(lambda x: x.sum() if x.isna().sum() == 0 else np.nan)
    )

    # Calculate +DI and -DI
    df["+DI"] = 100 * df["Smoothed_+DM"] / df["Smoothed_TR"]
    df["-DI"] = 100 * df["Smoothed_-DM"] / df["Smoothed_TR"]

    # Calculate DX
    df["DX"] = 100 * np.abs(df["+DI"] - df["-DI"]) / (df["+DI"] + df["-DI"])

    return df


def study_predicted_vs_actual_volatility(
    df: pd.DataFrame,
    iv_col: str,
    actual_change_col: str,
    multiplier: float,
    divide_actual_by: float = 100,
) -> pd.DataFrame:
    df = df.copy()
    df["predicted_change"] = (df[iv_col] / multiplier).shift(1)
    df["actual_change"] = df[actual_change_col] / divide_actual_by
    df["predicted_vs_actual_gap"] = df["predicted_change"] - df["actual_change"]
    return df
