import pandas as pd
import warnings
from datetime import datetime, timedelta
import re


# Cleaning the csv files
def parse_option_string_with_digits(option_string: str) -> dict[str, str]:
    """
    Parse the given option string to identify the underlying asset, expiry date, strike price, and option type.
    This version accommodates underlying symbols that may contain digits.

    Parameters:
        option_string (str): The option string to be parsed.

    Returns:
        dict[str, str]: A dictionary containing the parsed information.
    """
    # Using a non-greedy match for the underlying and a greedy match for the strike
    pattern = r"(.+?)(\d{2}[a-zA-Z]{3}\d{2})(\d+)([a-zA-Z]+)"
    match = re.match(pattern, option_string)

    if match:
        groups = match.groups()
        return {
            "underlying": groups[0],
            "expiry": groups[1],
            "strike": groups[2],
            "option_type": groups[3].upper(),
        }
    else:
        print(f"ERROR IN OPTION STRING {option_string}")
        return {"error": "Invalid option string format"}


def round_to_next_minute(time_str):
    """
    Round a time string (HH:MM:SS) to the next minute.
    """
    time_obj = datetime.strptime(time_str, "%H:%M:%S")
    # Add enough seconds to round to the next minute
    rounded_time_obj = time_obj + timedelta(seconds=(60 - time_obj.second))
    rounded_time_str = rounded_time_obj.strftime("%H:%M:%S")
    return rounded_time_str


def process_daily_prices(df):
    # Suppress the specific UserWarning
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=UserWarning)
        # Filtering out tickers that end in either -I.NFO or -II.NFO
        df = df[~df.Ticker.str.contains(r"(I|II|III|FUT).NFO$")]

        # Filtering for only indices
        df = df[df.Ticker.str.contains(r"^(.*?)NIFTY")]

    df[["underlying", "expiry", "strike", "option_type"]] = (
        df.Ticker.apply(parse_option_string_with_digits).apply(pd.Series).values
    )
    df.strike = df.strike.apply(int)
    df["Time"] = df["Time"].apply(round_to_next_minute)
    df["Date"] = pd.to_datetime(df.Date, dayfirst=True)
    df["Time"] = pd.to_timedelta(df.Time)
    df["timestamp"] = df["Date"] + df["Time"]
    df = df.drop(columns=["Ticker", "Date", "Time"])
    df = df[
        [
            "timestamp",
            "underlying",
            "expiry",
            "strike",
            "option_type",
            "Open",
            "High",
            "Low",
            "Close",
            "Volume",
            "Open Interest",
        ]
    ]
    df.columns = [name.lower() for name in df.columns]
    df.rename(columns={"open interest": "open_interest"}, inplace=True)

    return df
