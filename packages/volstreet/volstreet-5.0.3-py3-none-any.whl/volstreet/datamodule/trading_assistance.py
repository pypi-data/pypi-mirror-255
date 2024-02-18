from datetime import timedelta
from volstreet.datamodule.eod_client import EODClient
from volstreet.config import logger
from volstreet.datamodule.analysis import analyser, ratio_analysis
from volstreet.exceptions import ApiKeyNotFound
from volstreet.utils import current_time


def get_summary_ratio(
    target_symbol, benchmark_symbol, frequency="D", periods_to_avg=50, client=None
):
    try:
        if client is None:
            try:
                dc = EODClient()
            except ApiKeyNotFound:
                return None
        else:
            dc = client

        from_date = current_time() - timedelta(days=2 * periods_to_avg)
        from_date = from_date.date().strftime("%Y-%m-%d")
        benchmark = dc.get_data(benchmark_symbol, from_date=from_date)
        target = dc.get_data(target_symbol, from_date=from_date)
        benchmark = analyser(benchmark, frequency=frequency)
        target = analyser(target, frequency=frequency)
        ratio = ratio_analysis(target, benchmark, periods_to_avg=periods_to_avg)
        return ratio.loc["Summary", "Ratio"]
    except Exception as e:
        logger.error(f"Error in get_summary_ratio: {e}")
        return None
