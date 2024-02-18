import pandas as pd
import numpy as np
from volstreet.utils import current_time
from volstreet.datamodule.analysis import analyser


def retain_name(func):
    def wrapper(df, *args, **kwargs):
        try:
            name = df.name
        except AttributeError:
            name = None
        df = func(df, *args, **kwargs)
        df.name = name
        return df

    return wrapper


@retain_name
def generate_streak(df, query):
    df = df.copy(deep=True)

    # Create a boolean series with the query
    _bool = df.query(f"{query}")
    df["result"] = df.index.isin(_bool.index)
    df["start_of_streak"] = (df["result"].ne(df["result"].shift())) & (
        df["result"] == True
    )
    df["streak_id"] = df.start_of_streak.cumsum()
    df.loc[df["result"] == False, "streak_id"] = np.nan
    df["streak_count"] = df.groupby("streak_id").cumcount() + 1

    return df[df.result == True].drop(columns=["start_of_streak"])


@retain_name
def gambler(instrument, freq, query):
    """
    This function takes in instrument dataframe, frequency, and query and returns the streaks for the query.
    The instrument df should be a dataframe with daily closing values.
    The query should be a string with the following format: '{column} {operator} {value}'.
    The column should be a column in the instrument dataframe.
    The operator should be one of the following: '>', '<', '>=', '<=', '==', '!='.
    The value should be a number.
    """

    def generate_frequency(frequency):
        if frequency.startswith("W") or frequency.startswith("M"):
            if len(frequency) == 1:
                days = ["mon", "tue", "wed", "thu", "fri"]
                return [f"{frequency}-{day}" for day in days]
            else:
                return [frequency]
        else:
            return [frequency]

    def _calculate_streak_summary(df, frequency, query):
        # Calculate the streak summary

        if df.index[-1].replace(hour=15, minute=30) > current_time():
            df = df.iloc[:-1]
        check_date = df.index[-1]
        total_instances = len(df)
        df = generate_streak(df, query)
        total_streaks = len(df)
        number_of_positive_events = total_instances - total_streaks
        event_occurrence_pct = number_of_positive_events / total_instances

        df = (
            df.reset_index()
            .groupby("streak_id")
            .agg({"date": ["min", "max"], "streak_count": "max"})
            .reset_index()
        )
        df.columns = ["streak_id", "start_date", "end_date", "streak_count"]

        # Check if there is an ongoing streak
        current_streak = (
            df.iloc[-1].streak_count if df.iloc[-1].end_date == check_date else None
        )

        # Calculating the percentile of the current streak
        if current_streak:
            current_streak_percentile = (
                df.streak_count.sort_values().values.searchsorted(current_streak)
                / len(df)
            )
        else:
            current_streak_percentile = 0

        return {
            "freq": frequency,  # Use the given freq value instead of df.iloc[-1].name
            "total_instances": total_instances,
            "total_streaks": total_streaks,
            "event_occurrence": event_occurrence_pct,
            "longest_streak": df.streak_count.max(),
            "longest_streak_start": df.start_date[df.streak_count.idxmax()],
            "longest_streak_end": df.end_date[df.streak_count.idxmax()],
            "current_streak": current_streak,
            "current_streak_percentile": current_streak_percentile,
            "dataframe": df,
        }

    def print_streak_summary(summary):
        print(
            f"Query: {dataframe.name} {query}\n"
            f"Frequency: {summary['freq']}\n"
            f"Total Instances: {summary['total_instances']}\n"
            f"Total Streaks: {summary['total_streaks']}\n"
            f"Event Occurrence: {summary['event_occurrence']}\n"
            f"Longest Streak: {summary['longest_streak']}\n"
            f"Longest Streak Start: {summary['longest_streak_start']}\n"
            f"Longest Streak End: {summary['longest_streak_end']}\n"
            f"Current Streak: {summary['current_streak']}\n"
            f"Current Streak Percentile: {summary['current_streak_percentile']}\n"
        )

    freqs = generate_frequency(freq)
    streaks = []
    for freq in freqs:
        dataframe = analyser(instrument, frequency=freq)
        if query == "abs_change":
            recommended_threshold = (
                dataframe.abs_change.mean() * 0.70
            )  # 0.70 should cover 50% of the data
            # (mildly adjusted for abnormal distribution)
            recommended_threshold = round(recommended_threshold, 2)
            recommended_sign = (
                ">" if dataframe.iloc[-2].abs_change > recommended_threshold else "<"
            )
            query = f"abs_change {recommended_sign} {recommended_threshold}"
            print(f"Recommended query: {query}\n")
        streak_summary = _calculate_streak_summary(dataframe, freq, query)
        streaks.append(streak_summary)
        print_streak_summary(streak_summary)
    # Convert the list of dictionaries to a list of DataFrames
    streaks_df = [pd.DataFrame([streak]) for streak in streaks]

    # Concatenate the list of DataFrames
    return (
        pd.concat(streaks_df)
        .sort_values("longest_streak", ascending=False)
        .reset_index(drop=True)
    )
