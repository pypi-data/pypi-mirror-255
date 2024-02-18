import numpy as np
import pandas as pd
import re
from datetime import datetime, time, timedelta
from volstreet.blackscholes import calculate_strangle_iv


class StockMockAnalyzer:
    def __init__(self, backtester):
        self.backtester = backtester

    def clean_stockmock_excel(self, filename):
        index_name = re.search(r"(\w+)_stockmock_straddle", filename).group(1).upper()
        df = read_stockmock_excel_file(filename)

        ceindex = ["CE" in entry for entry in df.columns].index(1)
        peindex = ["PE" in entry for entry in df.columns].index(1)

        df = df.set_axis(df.iloc[0], axis=1, copy=False)
        df.drop(df.index[0], inplace=True)

        strike = df.Strike.iloc[:, 0]
        df = df.filter(regex="Date|Exit|Entry")
        df.drop(columns=df.filter(regex="Fut").columns, inplace=True)
        df["Strike"] = strike

        if "Exit Time" not in df.columns:
            indices_to_insert = np.where(df.columns == "Exit Price")[0]
            for idx in indices_to_insert:
                df.insert(idx + 1, "Exit Time", "15:29")

        renamecols = [
            "Date",
            "Expiry",
            "VixEntry",
            "VixExit",
            "EntrySpot",
            "ExitSpot",
            "CallEntryPrice" if ceindex < peindex else "PutEntryPrice",
            "CallExitPrice" if ceindex < peindex else "PutExitPrice",
            "CallExitTime" if ceindex < peindex else "PutExitTime",
            "PutEntryPrice" if ceindex < peindex else "CallEntryPrice",
            "PutExitPrice" if ceindex < peindex else "CallExitPrice",
            "PutExitTime" if ceindex < peindex else "CallExitTime",
            "Strike",
        ]

        if ceindex == peindex:
            raise Exception("Cannot determine whether call column is before put column")

        df.columns = renamecols
        df["Strike"] = df.Strike.apply(lambda x: int(x.rstrip("PE|CE")))

        # Process data
        df["TotalEntryPrice"] = df.CallEntryPrice + df.PutEntryPrice
        df["TotalExitPrice"] = df.CallExitPrice + df.PutExitPrice
        df["Profit"] = df.TotalEntryPrice - df.TotalExitPrice

        # Handle dates
        df["Date"] = [
            *map(lambda x: x.date(), pd.to_datetime(df.Date, format="%Y-%m-%d"))
        ]
        df.set_index("Date", inplace=True)
        df.index = pd.to_datetime(df.index)
        df["Expiry"] = df.index.to_series().apply(
            lambda x: self.backtester.fetch_nearest_expiry_from_date(
                index_name, x
            ).replace(hour=15, minute=30)
        )
        df["TimeToExpiry"] = df.Expiry - df.index.map(
            lambda x: x.replace(hour=9, minute=15)
        )

        cols = [
            "Expiry",
            "TimeToExpiry",
            "VixEntry",
            "VixExit",
            "EntrySpot",
            "ExitSpot",
            "Strike",
            "CallEntryPrice",
            "PutEntryPrice",
            "TotalEntryPrice",
            "CallExitPrice",
            "PutExitPrice",
            "TotalExitPrice",
            "CallExitTime",
            "PutExitTime",
            "Profit",
        ]

        return df[cols]

    @staticmethod
    def process_stockmock_df(df, spotoneminutedf, maxtrendsl=0.3, maxtrendprofit=0.7):
        df = df.copy()
        spotoneminutedf = spotoneminutedf.copy()

        spotoneminutedf = (
            spotoneminutedf.resample("1min")
            .last()
            .interpolate(method="time")
            .between_time("09:15", "15:30")
        )
        oneminutedf_grouped = pd.DataFrame(
            spotoneminutedf.groupby(spotoneminutedf.index.date), columns=["date", "df"]
        )
        oneminutedf_grouped = oneminutedf_grouped.set_index(
            pd.to_datetime(oneminutedf_grouped.date)
        ).drop("date", axis=1)

        def locate(df, datetime):
            try:
                price = df.loc[datetime].close
            except KeyError:
                if df.loc[datetime.date()].empyty():
                    print(f"No price df for day: {datetime.date()}. Returning None.")
                    return None
                else:
                    newdatetime = df[df.index > datetime].iloc[0].name
                    price = df[df.index > datetime].iloc[0].close
                    print(
                        f"No price found for {datetime}. Substituting with {newdatetime}.\n"
                    )
            return price

        def fetchexitprice(row):
            if row.SL_type == "NA":
                slprice = row.ExitSpot
            elif row.SL_type == "Call":
                slprice = locate(
                    spotoneminutedf, datetime.combine(row.name, row.CallExitTime)
                )
            elif row.SL_type == "Put":
                slprice = locate(
                    spotoneminutedf, datetime.combine(row.name, row.PutExitTime)
                )
            elif row.SL_type.startswith("Both"):
                if row.CallExitTime < row.PutExitTime:
                    slprice = locate(
                        spotoneminutedf, datetime.combine(row.name, row.CallExitTime)
                    )
                else:
                    slprice = locate(
                        spotoneminutedf, datetime.combine(row.name, row.PutExitTime)
                    )

            closeprice = locate(
                spotoneminutedf, datetime.combine(row.name, time(15, 28))
            )

            return slprice, closeprice

        def sltype(callexittime, putexittime):
            if all([callexittime == "No SL", putexittime == "No SL"]):
                return "NA"
            elif callexittime != "No SL" and putexittime != "No SL":
                if callexittime < putexittime:
                    return "Both. First:Call"
                else:
                    return "Both. First:Put"
            elif callexittime != "No SL" and putexittime == "No SL":
                return "Call"
            else:
                return "Put"

        def trend_checker(
            row,
            stoploss_max_trend=maxtrendsl,
            take_profit_max_trend=maxtrendprofit,
            _print=False,
        ):
            if row.SL_type == "NA":
                return None, None, None, None, None, None

            pricedf = oneminutedf_grouped.loc[row.name].df

            if row.SL_type.startswith("Both"):
                sltype = row.SL_type.split(":")[1]
            else:
                sltype = row.SL_type

            timeofexit = datetime.combine(row.name, row[f"{sltype}ExitTime"])
            niftyatexit = row.SpotAtFirstSL
            extreme_price_label = "max" if sltype == "Call" else "min"
            trend_modifier = 1 if sltype == "Call" else -1

            # Extreme price and its time
            price_extreme = (
                pricedf.loc[timeofexit:].close.max()
                if sltype == "Call"
                else pricedf.loc[timeofexit:].close.min()
            )
            time_of_extreme_price = (
                pricedf.loc[timeofexit:].close.idxmax()
                if sltype == "Call"
                else pricedf.loc[timeofexit:].close.idxmin()
            )

            # SL and profit price and time
            def get_price_time(
                pricedf, timeofexit, niftyatexit, price_multiplier, condition
            ):
                target_price = niftyatexit * price_multiplier
                price_condition = condition(
                    pricedf.loc[timeofexit:].close, target_price
                )
                target_array = pricedf.loc[timeofexit:].close[price_condition]
                return (
                    (target_price, target_array.iloc[0], target_array.index[0])
                    if not target_array.empty
                    else (target_price, False, False)
                )

            # Stoploss price and time
            stoploss_multiplier = (
                1 + (-1 if sltype == "Call" else 1) * stoploss_max_trend / 100
            )
            stoploss_condition = lambda x, y: x < y if sltype == "Call" else x > y
            (
                stoploss_price,
                stoploss_price_matched,
                time_of_maxtrend_sl,
            ) = get_price_time(
                pricedf,
                timeofexit,
                niftyatexit,
                stoploss_multiplier,
                stoploss_condition,
            )

            # Profit target price and time
            profit_target_multiplier = 1 + trend_modifier * take_profit_max_trend / 100
            profit_target_condition = lambda x, y: x > y if sltype == "Call" else x < y
            (
                profit_target_price,
                profit_target_price_matched,
                time_of_maxtrend_pt,
            ) = get_price_time(
                pricedf,
                timeofexit,
                niftyatexit,
                profit_target_multiplier,
                profit_target_condition,
            )

            if stoploss_price_matched and profit_target_price_matched:
                if time_of_maxtrend_sl < time_of_maxtrend_pt:
                    max_trend_sl_hit = True
                else:
                    max_trend_sl_hit = False
            elif stoploss_price_matched:
                max_trend_sl_hit = True
            else:
                max_trend_sl_hit = False

            extreme_change_after_sl = (
                ((price_extreme / niftyatexit) - 1) * 100 * trend_modifier
            )
            nifty_close_price = row.ExitSpot
            end_change_after_sl = (
                ((nifty_close_price / niftyatexit) - 1) * 100 * trend_modifier
            )

            if max_trend_sl_hit:
                trend_captured = (
                    (stoploss_price / niftyatexit - 1) * 100 * trend_modifier
                )
            else:
                if profit_target_price_matched:
                    trend_captured = (
                        (profit_target_price / niftyatexit - 1) * 100 * trend_modifier
                    )
                else:
                    trend_captured = (
                        (nifty_close_price / niftyatexit - 1) * 100 * trend_modifier
                    )
            if _print is True:
                print(
                    f"Day: {row.name}, SL: {sltype}, Nifty at exit: {niftyatexit}, Stoploss price: {stoploss_price}, "
                    f"Stoploss price matched: {stoploss_price_matched}, Time of max trend SL: {time_of_maxtrend_sl}, "
                    f"Nifty {extreme_price_label} price: {price_extreme}, Time of {extreme_price_label} price: {time_of_extreme_price}, "
                    f"Nifty close price: {nifty_close_price}, {extreme_price_label.capitalize()} change after SL: {extreme_change_after_sl}, "
                    f"End change after SL: {end_change_after_sl}"
                )

            return (
                end_change_after_sl,
                extreme_change_after_sl,
                max_trend_sl_hit,
                stoploss_price,
                time_of_maxtrend_sl,
                trend_captured,
            )

        # Actual Analysis After Function Definitions

        df.loc[((df.CallExitTime.isna()) & (df.PutExitTime.isna())), "SL_hit"] = False
        df.loc[~((df.CallExitTime.isna()) & (df.PutExitTime.isna())), "SL_hit"] = True
        # df['SL_contribution'] = df.Profit_SL - df.Profit_NOSL
        df["CallExitTime"] = df.CallExitTime.fillna("No SL").apply(
            lambda x: "No SL" if x == "No SL" else datetime.strptime(x, "%H:%M").time()
        )
        df["PutExitTime"] = df.PutExitTime.fillna("No SL").apply(
            lambda x: "No SL" if x == "No SL" else datetime.strptime(x, "%H:%M").time()
        )
        df["SL_type"] = df.apply(
            lambda row: sltype(row.CallExitTime, row.PutExitTime), axis=1
        )
        df["FirstSL"] = df.SL_type.where(
            df.SL_type.str.fullmatch("Call|Put"), df.SL_type.str.lstrip("Both. First:")
        )
        df[["SpotAtFirstSL", "SpotClosePrice"]] = df.apply(
            lambda row: fetchexitprice(row), axis=1
        ).to_list()
        df["ChangeFirstSL"] = ((df.SpotAtFirstSL / df.EntrySpot) - 1) * 100
        df["AbsChangeFirstSL"] = abs(df.ChangeFirstSL)
        df[
            [
                "TrendAtClose",
                "MaxTrend",
                "MaxTrendSL",
                "MaxTrendSLPrice",
                "MaxTrendSLTime",
                "TrendCaptured",
            ]
        ] = df.apply(lambda row: trend_checker(row), axis=1).to_list()
        df["ProfitPct"] = (df.Profit / df.EntrySpot) * 100
        df["NAV"] = ((df.ProfitPct + 100) / 100).dropna().cumprod()
        df["Max_NAV"] = df.NAV.cummax()
        df["Drawdown"] = ((df.NAV / df.Max_NAV) - 1) * 100
        df["EntryIV"] = df.apply(
            lambda row: calculate_strangle_iv(
                row.CallEntryPrice,
                row.PutEntryPrice,
                row.EntrySpot,
                time_left=row.TimeToExpiry / timedelta(days=365),
                strike=row.Strike,
            )[2],
            axis=1,
        )
        df["CallExitTime"] = df.apply(
            lambda row: datetime.combine(row.name, row.CallExitTime)
            if row.CallExitTime != "No SL"
            else "No SL",
            axis=1,
        )
        df["PutExitTime"] = df.apply(
            lambda row: datetime.combine(row.name, row.PutExitTime)
            if row.PutExitTime != "No SL"
            else "No SL",
            axis=1,
        )
        df["FirstSLTime"] = np.where(
            df.FirstSL == "Call",
            df.CallExitTime,
            np.where(
                df.FirstSL == "Put",
                df.PutExitTime,
                df.index.map(lambda x: datetime.combine(x, time(15, 28))),
            ),
        )

        def convert_to_datetime(value):
            if isinstance(value, int):
                # Assuming the integer represents a Unix timestamp in nanoseconds
                return datetime.utcfromtimestamp(
                    value / 1e9
                )  # Divide by 1e9 to convert to seconds
            return value

        df["FirstSLTime"] = df.FirstSLTime.apply(convert_to_datetime)

        cols = [
            "EntrySpot",
            "EntryIV",
            "Strike",
            "Expiry",
            "TimeToExpiry",
            "CallEntryPrice",
            "PutEntryPrice",
            "CallExitPrice",
            "PutExitPrice",
            "CallExitTime",
            "PutExitTime",
            "SL_hit",
            "FirstSLTime",
            "SL_type",
            "FirstSL",
            "SpotAtFirstSL",
            "ChangeFirstSL",
            "AbsChangeFirstSL",
            "ExitSpot",
            "SpotClosePrice",
            "TrendAtClose",
            "MaxTrend",
            "MaxTrendSL",
            "MaxTrendSLPrice",
            "MaxTrendSLTime",
            "TrendCaptured",
            "Profit",
            "ProfitPct",
            "NAV",
            "Max_NAV",
            "Drawdown",
        ]

        return df[cols]


def read_stockmock_excel_file(filename):
    filename_without_extension = filename.split(".")[0]
    return pd.read_excel(f"data\\{filename_without_extension}.xlsx", sheet_name=2)
