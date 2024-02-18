from eod import EodHistoricalData
import os
from volstreet.exceptions import ApiKeyNotFound
import pandas as pd
from datetime import datetime, timedelta


class EODClient:
    def __init__(self, api_key=None):
        if api_key is None:
            try:  # Try to get the api key from the environment variable
                api_key = os.getenv("EOD_API_KEY")
            except KeyError:
                raise ApiKeyNotFound(
                    "EOD API Key not found. Please set the API key in environment variables or pass it as an argument."
                )
        self.api_key = api_key
        self.client = EodHistoricalData(api_key=api_key)

    @staticmethod
    def parse_symbol(symbol):
        symbol_dict = {
            "NIFTY": "NSEI.INDX",
            "NIFTY 50": "NSEI.INDX",
            "NIFTY50": "NSEI.INDX",
            "BANKNIFTY": "NSEBANK.INDX",
            "NIFTY BANK": "NSEBANK.INDX",
            "NIFTYBANK": "NSEBANK.INDX",
            "FINNIFTY": "CNXFIN.INDX",
            "NIFTY FIN SERVICE": "CNXFIN.INDX",
            "NIFTY MIDCAP 100": "NIFMDCP100",
            "NIFTY MIDCAP SELECT": "NIFTYMIDSELECT",
            "NIFTY SMALLCAP 100": "NIFSMCP100",
            "NIFTY SMALLCAP 250": "NISM250",
            "VIX": "NIFVIX.INDX",
            "USVIX": "VIX.INDX",
            "US VIX": "VIX.INDX",
        }
        symbol = symbol.upper()
        if "." not in symbol:
            if symbol in symbol_dict:
                symbol = symbol_dict[symbol]
            else:
                symbol = symbol + ".NSE"
        return symbol

    def get_data(self, symbol, from_date="2011-01-01", return_columns=None):
        name = symbol.split(".")[0] if "." in symbol else symbol

        symbol = self.parse_symbol(symbol)

        if return_columns is None:
            return_columns = ["open", "close", "gap", "intra", "abs_gap", "abs_intra"]

        resp = self.client.get_prices_eod(
            symbol, period="d", order="a", from_=from_date
        )
        df = pd.DataFrame(resp)
        df["date"] = pd.to_datetime(df["date"])
        df.set_index(df.date, inplace=True)
        df["p_close"] = df.close.shift(1)
        df["gap"] = (df.open / df.p_close - 1) * 100
        df["intra"] = (df.close / df.open - 1) * 100
        df["abs_gap"] = abs(df.gap)
        df["abs_intra"] = abs(df.intra)
        df = df.loc[:, return_columns]
        df.name = name
        return df

    def get_intraday_data(
        self,
        symbol,
        interval,
        from_date="2011-01-01",
        to_date=None,
        return_columns=None,
        time_zone="Asia/Kolkata",
    ):
        name = symbol.split(".")[0] if "." in symbol else symbol

        symbol = self.parse_symbol(symbol)

        if return_columns is None:
            return_columns = ["open", "high", "low", "close"]

        to_date = pd.to_datetime(to_date) if to_date is not None else datetime.now()
        from_date = pd.to_datetime(from_date)

        resp_list = []
        while to_date.date() > from_date.date():
            _to_date_temp = (
                from_date + timedelta(days=120)
                if to_date - from_date > timedelta(days=120)
                else to_date
            )
            resp = self.client.get_prices_intraday(
                symbol,
                interval=interval,
                from_=str(int(from_date.timestamp())),
                to=str(int(_to_date_temp.timestamp())),
            )

            resp_list.extend(resp)
            # If the last date in the resp is greater than the temp to_date, then we will advance the from_date
            # to the last date in the resp. Else, we will advance the from_date by 120 days.
            if (
                datetime.fromisoformat(resp[-1]["datetime"]).date()
                > _to_date_temp.date()
            ):
                from_date = datetime.fromisoformat(resp[-1]["datetime"])
                print(
                    f"Given more data than requested. Advancing from_date to {from_date}"
                )
            else:
                from_date = _to_date_temp

        df = pd.DataFrame(resp_list)
        df = df.drop_duplicates()
        df.index = (
            pd.to_datetime(df.datetime).dt.tz_localize("UTC").dt.tz_convert(time_zone)
        )
        df.index = df.index.tz_localize(None)
        df = df[return_columns]
        df.name = name
        return df
