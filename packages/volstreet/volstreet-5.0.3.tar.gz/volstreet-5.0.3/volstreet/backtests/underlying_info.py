import pandas as pd
from datetime import datetime
import pickle
from volstreet.config import logger, historical_expiry_dates
from volstreet.backtests.database import DataBaseConnection


class UnderlyingInfo:
    def __init__(self, name):
        self.name = name.upper()
        self.base = self._get_base()
        self.expiry_dates = self._get_expiry_dates()

    def _get_base(self):
        if self.name in ["NIFTY", "FINNIFTY"]:
            return 50
        elif self.name == "BANKNIFTY":
            return 100
        elif self.name == "MIDCPNIFTY":
            return 25
        else:
            raise ValueError("Invalid index name")

    def _get_expiry_dates(self):
        index_expiry_dates = historical_expiry_dates[self.name.upper()]
        index_expiry_dates = [
            *map(
                lambda x: datetime.strptime(x, "%d%b%y").replace(hour=15, minute=30),
                index_expiry_dates,
            )
        ]
        return pd.DatetimeIndex(sorted(index_expiry_dates))


def extend_expiry_dates() -> None:
    """Extend the expiry dates which are stored in the index_expiries.pkl file."""

    dbc = DataBaseConnection()

    with open("volstreet\\historical_info\\index_expiries.pkl", "rb") as file:
        all_expiry_dates = pickle.load(file)

    for underlying in ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"]:
        index_expiry_dates = all_expiry_dates[underlying]
        new_list = dbc.fetch_historical_expiries(underlying)
        combined_list = [*set(index_expiry_dates + new_list)]
        all_expiry_dates[underlying] = combined_list
        logger.info(f"Extended expiry dates for {underlying}")

    with open("volstreet\\historical_info\\index_expiries.pkl", "wb") as file:
        pickle.dump(all_expiry_dates, file)
