import numpy as np
from datetime import datetime, timedelta, time
from threading import Thread
from time import sleep
from typing import Optional
from volstreet.config import logger
from volstreet.utils.core import (
    current_time,
    find_strike,
    time_to_expiry,
    check_for_weekend,
    calculate_ema,
    strike_range_different,
    filter_orderbook_by_time,
)
from volstreet.utils.communication import notifier, log_error
from volstreet.utils.data_io import save_json_data
from volstreet.exceptions import IntrinsicValueError
from volstreet.blackscholes import simulate_price, calculate_strangle_iv
from volstreet.dealingroom import SharedData, fetch_orderbook_if_needed
from volstreet.angel_interface.interface import (
    fetch_book,
    lookup_and_return,
    fetch_historical_prices,
    increase_robustness,
)
from volstreet.angel_interface.active_session import ActiveSession
from volstreet.trade_interface import (
    SyntheticFuture,
    Strangle,
    Straddle,
    Action,
    OptionType,
    Option,
    Index,
    Stock,
    IndiaVix,
    place_option_order_and_notify,
    process_stop_loss_order_statuses,
    cancel_pending_orders,
)
from volstreet.strategies.helpers import (
    sleep_until_next_action,
    round_shares_to_lot_size,
    most_equal_strangle,
    DeltaPosition,
    load_current_straddle,
    calculate_pnl_for_strategy,
    most_even_delta_strangle,
    is_in_final_stage,
    check_for_universal_exit,
    check_for_move,
    identify_new_option,
    check_for_overlap,
    move_one_leg,
)
from volstreet.strategies.error_handling import exit_on_error


@exit_on_error
def delta_hedged_strangle_lite(
    underlying: Index | Stock,
    quantity_in_lots: int,
    target_delta: float = 0.25,
    sl_pct: float = 0.25,
    end_time: tuple = (15, 00),
    itm_steps_allowed: int = 2,
    final_sl_pct: float = 0.4,
    strategy_tag: str = "Equal delta strangle",
    notification_url: str = None,
):
    """Strangle with stoploss based delta hedging"""

    logger.info(
        f"{underlying.name} Starting delta hedged strangle with params: {locals()}"
    )
    target_strangle = None
    while target_strangle is None and current_time().time() < time(15, 25):
        target_strangle, _ = most_even_delta_strangle(
            underlying, delta_range=(target_delta - 0.05, target_delta + 0.05)
        )
        sleep(1)
    if target_strangle is None:
        notifier(
            f"{underlying.name} Could not find strangle with delta {target_delta}. Exiting.",
            notification_url,
        )
        return

    notifier(
        f"{underlying.name} Target strangle: {target_strangle}",
        notification_url,
    )
    current_call_avg, current_put_avg = place_option_order_and_notify(
        target_strangle,
        "SELL",
        quantity_in_lots,
        "LIMIT",
        order_tag=strategy_tag,
        webhook_url=notification_url,
        return_avg_price=True,
    )
    while current_time().time() < time(*end_time):
        final_stage = is_in_final_stage(underlying, target_strangle, itm_steps_allowed)
        universal_exit = check_for_universal_exit(
            target_strangle,
            current_call_avg,
            current_put_avg,
            final_sl_pct,
            final_stage,
        )
        if universal_exit:
            notifier(
                f"{underlying.name} Universal exit triggered. Exiting.",
                notification_url,
            )
            break
        sl_pct = final_sl_pct if final_stage else sl_pct
        option_to_move = check_for_move(
            target_strangle, current_call_avg, current_put_avg, sl_pct
        )
        if option_to_move:
            notifier(
                f"{underlying.name} move detected. Need to move {option_to_move.option_type}. ",
                notification_url,
            )
            new_option = identify_new_option(
                underlying, target_strangle, option_to_move
            )
            overlap = check_for_overlap(
                underlying, new_option, target_strangle, itm_steps_allowed
            )
            if overlap:
                notifier(
                    f"{underlying.name} max modifications reached. Exiting.",
                    notification_url,
                )
                break
            notifier(
                f"{underlying.name} {strategy_tag} Moving {option_to_move} to {new_option}",
                notification_url,
            )
            target_strangle, avg_price = move_one_leg(
                underlying,
                target_strangle,
                option_to_move,
                new_option,
                quantity_in_lots,
                strategy_tag,
                notification_url,
            )
            if option_to_move.option_type == OptionType.CALL:
                current_call_avg = avg_price
                current_put_avg = target_strangle.put_option.fetch_ltp()
            else:
                current_put_avg = avg_price
                current_call_avg = target_strangle.call_option.fetch_ltp()
            logger.info(
                f"Updated strangle to {target_strangle} with call avg {current_call_avg} and put avg {current_put_avg}"
            )
        sleep(1)

    place_option_order_and_notify(
        target_strangle,
        "BUY",
        quantity_in_lots,
        "LIMIT",
        order_tag=strategy_tag,
        webhook_url=notification_url,
    )


@exit_on_error
@increase_robustness
def delta_hedged_strangle(
    underlying: Index | Stock,
    tracking_strikes: int,
    max_exposure: int,
    target_delta: float,
    delta_interval_minutes: int | float = 1,
    delta_threshold_pct: float = 0.02,
    exit_time: Optional[tuple] = (15, 29),
    notification_url: Optional[str] = None,
    strategy_tag: Optional[str] = "Delta hedged strangle",
):
    """Strangle with continuous delta hedging."""
    start_time = current_time()
    base_exposure = max_exposure / 1.2

    if time_to_expiry(underlying.current_expiry, in_days=True) < 1:
        exit_time = min([tuple(exit_time), (14, 40)])
        logger.info(
            f"{underlying.name} exit time changed to {exit_time} because expiry is today"
        )

    spot_price = underlying.fetch_ltp()

    # find_strike is being used for convenience. It is a way to custom round numbers
    max_qty_shares = round_shares_to_lot_size(
        max_exposure / spot_price, underlying.lot_size
    )
    base_qty_shares = round_shares_to_lot_size(
        base_exposure / spot_price, underlying.lot_size
    )

    delta_threshold = delta_threshold_pct * base_qty_shares

    logger.info(
        f"---- {underlying.name} {strategy_tag} ----\n"
        f"{underlying.name} {strategy_tag} "
        f"max qty: {max_qty_shares}, "
        f"base qty: {base_qty_shares} "
        f"delta threshold: {delta_threshold}"
    )

    delta_position: DeltaPosition = DeltaPosition(
        underlying=underlying,
        base_exposure_qty=base_qty_shares,
        order_tag=strategy_tag,
        notifier_url=notification_url,
    )
    entry_priority = None
    while current_time().time() < time(*exit_time):
        if delta_position.cached_strikes is None or strike_range_different(
            underlying.get_active_strikes(tracking_strikes),
            delta_position.cached_strikes,
        ):
            delta_position.update_prospective_options(tracking_strikes)
            logger.info(
                f"{current_time()} {underlying.name} set active options and set "
                f"{len(delta_position.prospective_options)} prospective options"
            )
        delta_position.update_underlying()
        delta_position.set_recommended_qty(target_delta)
        delta_position.adjust_recommended_qty()
        delta_position.enter_positions(priority=entry_priority)
        delta_position.reset_trigger_flags()

        def interruption_condition():
            return abs(delta_position.aggregate_greeks().delta) > delta_threshold * 3.5
            # Hard coded 3.5 times to force action

        # Delta hedging begins here
        while not any(delta_position.exit_triggers.values()):
            sleep_until_next_action(
                delta_interval_minutes,
                exit_time,
                special_condition=interruption_condition,
            )

            if current_time().time() > time(*exit_time):
                delta_position.exit_triggers["end_time"] = True
                break

            delta_position.update_underlying()
            delta_position.record_position_status()
            aggregate_delta = (
                delta_position.aggregate_greeks().delta
            )  # The prices and greeks of the options are updated and cached here

            #  If aggregate delta breaches the threshold then adjust
            if abs(aggregate_delta) > delta_threshold:
                delta_position.set_hedge_options()
                message = (
                    f"{underlying.name} delta needs adjustment. "
                    f"Delta: {aggregate_delta}, "
                    f"Threshold: {delta_threshold}"
                )
                notifier(message, notification_url, "INFO")
                hedge_option, qty_to_hedge = delta_position.recommend_delta_action(
                    delta_threshold
                )
                if hedge_option:
                    # Check for breach
                    breach, entry_priority = delta_position.check_for_breach(
                        hedge_option.option_type, abs(qty_to_hedge), max_qty_shares
                    )
                    if breach:
                        # If max qty is breached and scan end time reached then exit
                        delta_position.exit_triggers["qty_breach_exit"] = True
                        message = (
                            f"{underlying.name} max qty breached. Shuffling position."
                        )
                        notifier(message, notification_url, "INFO")
                        break

                    hedge_option.execute_order(
                        qty_to_hedge,
                        hedge_option.cached_ltp,
                        strategy_tag,
                        notification_url,
                    )
                    message = (
                        f"{underlying.name} {strategy_tag} "
                        f"neutralized position with {hedge_option} "
                        f"qty: {qty_to_hedge}"
                    )
                    notifier(message, notification_url, "INFO")
                else:
                    message = (
                        f"{underlying.name} {strategy_tag} "
                        f"Delta breached but no hedge option available."
                    )
                    notifier(message, notification_url, "INFO")

    # Exiting the position
    message = f"{underlying.name} {strategy_tag} exit time reached."
    notifier(message, notification_url, "INFO")
    delta_position.exit_positions()
    delta_position.record_position_status()

    sleep(10)  # Wait for the exit orders to reflect with average prices
    orderbook: list = fetch_book("orderbook")
    filtered_orderbook = filter_orderbook_by_time(orderbook, start_time=start_time)
    total_pnl: float = calculate_pnl_for_strategy(
        data=filtered_orderbook,
        strategy_name="Delta hedged",
        underlying=underlying.name,
        flexible_matching=True,
    )

    notifier(
        f"{underlying.name} scan end time reached." f"Total pnl: {total_pnl}",
        notification_url,
        "INFO",
    )


@exit_on_error
def overnight_straddle(
    underlying: Index | Stock,
    quantity_in_lots: int,
    strike_offset: Optional[float] = 1,
    take_avg_price: Optional[bool] = False,
    avg_till: Optional[tuple] = (15, 28),
    notification_url: Optional[str] = None,
    strategy_tag: Optional[str] = "Overnight straddle",
):
    """Rollover overnight short straddle to the next expiry.
    Args:
        underlying (Index | Stock): Underlying object.
        quantity_in_lots (int): Quantity of the straddle in lots.
        strike_offset (float): Strike offset from the current strike.
        take_avg_price (bool): Take average price of the index over 5m timeframes.
        avg_till (tuple): Time till which to average the price.
        notification_url (str): Webhook URL to send notifications.
        strategy_tag (str): Tag to identify the strategy in the notification.
    """

    def is_next_day_expiry(tte: float) -> bool:
        return 1 < tte < 2

    def check_eligibility_for_overnight_straddle(effective_tte: float) -> bool:
        after_weekend = check_for_weekend(underlying.current_expiry)
        square_off_tte = (
            effective_tte - 1
        )  # Square off 1 day after because duration of the trade is 1 day

        logger.info(f"{underlying.name} current expiry tte is {effective_tte} days")

        if after_weekend:
            logger.info(f"{underlying.name} current expiry is after a weekend")
            return False

        if square_off_tte < 1:
            if is_next_day_expiry(effective_tte):
                logger.info(
                    f"{underlying.name} current expiry is next day so the trade is eligible on next expiry"
                )
                return True

            logger.info(
                f"{underlying.name} current expiry is today so the trade is not eligible"
            )
            return False

        logger.info(
            f"{underlying.name} current expiry has enough TTE to trade so the trade is eligible"
        )
        return True

    def get_expiry_to_trade_for_overnight_straddle(effective_tte: float) -> str:
        if is_next_day_expiry(effective_tte):
            return underlying.next_expiry
        return underlying.current_expiry

    # Entering main function
    effective_time_to_expiry = time_to_expiry(
        underlying.current_expiry, effective_time=True, in_days=True
    )
    eligible_for_short = check_eligibility_for_overnight_straddle(
        effective_time_to_expiry
    )

    # Taking avg price
    avg_ltp = None
    if take_avg_price:
        if current_time().time() < time(15, 00):
            notifier(
                f"{underlying.name} Cannot take avg price before 3pm. Try running the strategy after 3pm",
                notification_url,
                "ERROR",
            )
            raise Exception(
                "Cannot take avg price before 3pm. Try running the strategy after 3pm"
            )
        notifier(
            f"{underlying.name} Taking average price of the index over 5m timeframes.",
            notification_url,
            "INFO",
        )
        price_list = [underlying.fetch_ltp()]
        while current_time().time() < time(*avg_till):
            _ltp = underlying.fetch_ltp()
            price_list.append(_ltp)
            sleep(60)
        avg_ltp = np.mean(price_list)

    # Assigning vix
    vix = IndiaVix.fetch_ltp()

    # Initializing the straddle if eligible
    if eligible_for_short:
        # Assigning straddle with strike and expiry
        ltp = avg_ltp if avg_ltp else underlying.fetch_ltp()
        sell_strike = find_strike(ltp * strike_offset, underlying.base)
        expiry_to_trade = get_expiry_to_trade_for_overnight_straddle(
            effective_time_to_expiry
        )
        sell_straddle = Straddle(
            strike=sell_strike, underlying=underlying.name, expiry=expiry_to_trade
        )
        call_iv, put_iv, iv = sell_straddle.fetch_ivs()
        iv = iv * 100
        notifier(
            f"{underlying.name} Deploying overnight short straddle with {sell_straddle}. IV: {iv}, VIX: {vix}",
            notification_url,
            "INFO",
        )
    else:
        sell_strike = None
        expiry_to_trade = None
        sell_straddle = None
        notifier(
            f"{underlying.name} No straddle eligible for overnight short. VIX: {vix}",
            notification_url,
            "INFO",
        )

    # Loading current position
    buy_straddle = load_current_straddle(
        underlying_str=underlying.name,
        user_id=ActiveSession.obj.userId,
        file_appendix="overnight_positions",
    )

    trade_info_dict = {
        "Date": current_time().strftime("%d-%m-%Y %H:%M:%S"),
        "Underlying": underlying.name,
    }

    call_buy_avg, put_buy_avg = np.nan, np.nan
    call_sell_avg, put_sell_avg = np.nan, np.nan

    # Placing orders
    if buy_straddle is None and sell_straddle is None:
        notifier(f"{underlying.name} No trade required.", notification_url, "INFO")
    elif sell_straddle is None:  # only exiting current position
        notifier(
            f"{underlying.name} Exiting current position on {buy_straddle}.",
            notification_url,
            "INFO",
        )
        call_buy_avg, put_buy_avg = place_option_order_and_notify(
            buy_straddle,
            "BUY",
            quantity_in_lots,
            "LIMIT",
            order_tag=strategy_tag,
            webhook_url=notification_url,
            return_avg_price=True,
        )

    elif buy_straddle is None:  # only entering new position
        notifier(
            f"{underlying.name} Entering new position on {sell_straddle}.",
            notification_url,
            "INFO",
        )
        call_sell_avg, put_sell_avg = place_option_order_and_notify(
            sell_straddle,
            "SELL",
            quantity_in_lots,
            "LIMIT",
            order_tag=strategy_tag,
            webhook_url=notification_url,
            return_avg_price=True,
        )

    else:  # both entering and exiting positions
        if buy_straddle == sell_straddle:
            notifier(
                f"{underlying.name} Same straddle. No trade required.",
                notification_url,
                "INFO",
            )
            call_ltp, put_ltp = sell_straddle.fetch_ltp()
            call_buy_avg, put_buy_avg, call_sell_avg, put_sell_avg = (
                call_ltp,
                put_ltp,
                call_ltp,
                put_ltp,
            )
        else:
            notifier(
                f"{underlying.name} Buying {buy_straddle} and selling {sell_straddle}.",
                notification_url,
                "INFO",
            )
            call_buy_avg, put_buy_avg = place_option_order_and_notify(
                buy_straddle,
                "BUY",
                quantity_in_lots,
                "LIMIT",
                order_tag=strategy_tag,
                webhook_url=notification_url,
                return_avg_price=True,
            )
            call_sell_avg, put_sell_avg = place_option_order_and_notify(
                sell_straddle,
                "SELL",
                quantity_in_lots,
                "LIMIT",
                order_tag=strategy_tag,
                webhook_url=notification_url,
                return_avg_price=True,
            )

    trade_info_dict.update(
        {
            "Buy Straddle": buy_straddle,
            "Buy Call Price": call_buy_avg,
            "Buy Put Price": put_buy_avg,
            "Buy Total Price": call_buy_avg + put_buy_avg,
            "Sell Straddle": sell_straddle,
            "Sell Call Price": call_sell_avg,
            "Sell Put Price": put_sell_avg,
            "Sell Total Price": call_sell_avg + put_sell_avg,
        }
    )

    trade_data = {underlying.name: {"strike": sell_strike, "expiry": expiry_to_trade}}
    save_json_data(
        trade_data,
        f"{ActiveSession.obj.userId}\\{underlying.name}_overnight_positions.json",
    )  # Currently overwriting the file with the new data. Can be changed to use load_combine_save_json_data
    # to append the new data to the existing data.
    underlying.strategy_log[strategy_tag].append(trade_info_dict)


@exit_on_error
def buy_weekly_hedge(
    underlying: Index | Stock,
    quantity_in_lots: int,
    strike_offset: Optional[float] = 1,
    call_offset: Optional[float] = None,
    put_offset: Optional[float] = None,
    notification_url: Optional[str] = None,
    strategy_tag: Optional[str] = "Weekly hedge",
    override_expiry_day_restriction: Optional[bool] = False,
):
    """Buys next weeks strangle or straddle as a hedge. Offsets are the multipliers for the strike price.
    Example: 1.01 means 1.01 times the current price (1% above current price). If call_offset and put_offset are
    not provided, strike_offset is used for both call and put."""

    current_expiry_tte = time_to_expiry(underlying.current_expiry, in_days=True)
    # If current expiry is more than 1 day away, then the strategy is not eligible
    # unless override_expiry_day_restriction is True
    if current_expiry_tte > 1 and not override_expiry_day_restriction:
        logger.info(
            f"{underlying.name} not eligible for weekly hedge since it is not expiry day"
        )
        notifier(
            f"{underlying.name} not eligible for weekly hedge since it is not expiry day",
            notification_url,
            "INFO",
        )
        return

    ltp = underlying.fetch_ltp()
    if call_offset and put_offset:
        pass
    elif strike_offset:
        call_offset = put_offset = strike_offset
    else:
        raise Exception("Either strike_offset or call_offset and put_offset required")

    call_strike = find_strike(ltp * call_offset, underlying.base)
    put_strike = find_strike(ltp * put_offset, underlying.base)
    instrument = Strangle(
        call_strike, put_strike, underlying.name, underlying.next_expiry
    )

    call_iv, put_iv, iv = instrument.fetch_ivs()
    notifier(
        f"{underlying.name} Buying weekly hedge with {instrument}. IV: {iv}",
        notification_url,
        "INFO",
    )
    call_buy_avg, put_buy_avg = place_option_order_and_notify(
        instrument,
        "BUY",
        quantity_in_lots,
        "LIMIT",
        order_tag=strategy_tag,
        webhook_url=notification_url,
        return_avg_price=True,
    )

    trade_info_dict = {
        "Date": current_time().strftime("%d-%m-%Y %H:%M:%S"),
        "Underlying": underlying.name,
        "Buy Instrument": instrument,
        "Buy Call Price": call_buy_avg,
        "Buy Put Price": put_buy_avg,
        "Buy Total Price": call_buy_avg + put_buy_avg,
    }

    underlying.strategy_log[strategy_tag].append(trade_info_dict)


@exit_on_error
def biweekly_straddle(
    underlying: Index | Stock,
    quantity_in_lots: int,
    strike_offset: Optional[float] = 1,
    notification_url: Optional[str] = None,
    strategy_tag: Optional[str] = "Biweekly straddle",
    override_expiry_day_restriction: Optional[bool] = False,
):
    """Sells the far expiry straddle."""
    current_expiry_tte = time_to_expiry(underlying.current_expiry, in_days=True)
    # If current expiry is more than 1 day away, then the strategy is not eligible
    # unless override_expiry_day_restriction is True
    if current_expiry_tte > 1 and not override_expiry_day_restriction:
        logger.info(
            f"{underlying.name} not eligible for biweekly straddle since it is not expiry day"
        )
        notifier(
            f"{underlying.name} not eligible for biweekly straddle since it is not expiry day",
            notification_url,
            "INFO",
        )
        return

    # Loading current position
    buy_straddle = load_current_straddle(
        underlying_str=underlying.name,
        user_id=ActiveSession.obj.userId,
        file_appendix="biweekly_position",
    )

    # Initializing new position
    ltp = underlying.fetch_ltp()
    strike = find_strike(ltp * strike_offset, underlying.base)
    expiry = underlying.far_expiry
    sell_straddle = Straddle(strike, underlying.name, expiry)
    call_iv, put_iv, iv = sell_straddle.fetch_ivs()
    notifier(
        f"{underlying.name} Deploying biweekly straddle\n"
        f"Square up position: {buy_straddle}\n"
        f"New position: {sell_straddle}\n"
        f"IV: {iv}",
        notification_url,
        "INFO",
    )

    # Placing orders
    call_buy_avg, put_buy_avg = np.nan, np.nan

    if buy_straddle:
        call_buy_avg, put_buy_avg = place_option_order_and_notify(
            buy_straddle,
            "BUY",
            quantity_in_lots,
            "LIMIT",
            order_tag=strategy_tag,
            webhook_url=notification_url,
            return_avg_price=True,
        )

    call_sell_avg, put_sell_avg = place_option_order_and_notify(
        sell_straddle,
        "SELL",
        quantity_in_lots,
        "LIMIT",
        order_tag=strategy_tag,
        webhook_url=notification_url,
        return_avg_price=True,
    )

    position_to_save = {underlying.name: {"strike": strike, "expiry": expiry}}
    save_json_data(
        position_to_save,
        f"{ActiveSession.obj.userId}\\{underlying.name}_biweekly_position.json",
    )  # Currently overwriting the file with the new data. Can use load_combine_save_json_data in the future
    # to append the new data to the existing data. (Use case: multiple indices using the same file)

    trade_info_dict = {
        "Date": current_time().strftime("%d-%m-%Y %H:%M:%S"),
        "Underlying": underlying.name,
        "Buy Straddle": buy_straddle,
        "Buy Call Price": call_buy_avg,
        "Buy Put Price": put_buy_avg,
        "Buy Total Price": call_buy_avg + put_buy_avg,
        "Sell Straddle": sell_straddle,
        "Sell Call Price": call_sell_avg,
        "Sell Put Price": put_sell_avg,
        "Sell Total Price": call_sell_avg + put_sell_avg,
    }

    underlying.strategy_log[strategy_tag].append(trade_info_dict)


@exit_on_error
@increase_robustness
def intraday_strangle(
    underlying: Index | Stock,
    quantity_in_lots: int,
    call_strike_offset: Optional[float] = 0,
    put_strike_offset: Optional[float] = 0,
    strike_selection: Optional[str] = "equal",
    stop_loss: Optional[float | str] = "dynamic",
    call_stop_loss: Optional[float] = None,
    put_stop_loss: Optional[float] = None,
    exit_time: tuple[int, int] = (15, 29),
    sleep_time: Optional[int] = 5,
    seconds_to_avg: Optional[int] = 30,
    simulation_safe_guard: Optional[float] = 1.15,
    catch_trend: Optional[bool] = False,
    trend_qty_ratio: Optional[float] = 1,
    trend_strike_offset: Optional[float] = 0,
    trend_sl: Optional[float] = 0.003,
    trend_sl_on_option: Optional[bool] = 1.75,
    disparity_threshold: Optional[float] = 1000,
    place_sl_orders: Optional[bool] = False,
    move_sl_to_cost: Optional[bool] = False,
    place_orders_on_sl: Optional[bool] = False,
    convert_to_butterfly: Optional[bool] = False,
    conversion_method: Optional[str] = "pct",
    conversion_threshold_pct: Optional[float] = 0.175,
    take_profit: Optional[float] = 0,
    shared_data: Optional[SharedData] = None,
    notification_url: Optional[str] = None,
    strategy_tag: Optional[str] = "Intraday strangle",
):
    """Intraday strangle strategy. Trades strangle with stop loss. All offsets are in percentage terms.
    Parameters
    ----------
    underlying : Index | Stock
        Underlying object
    quantity_in_lots : int
        Quantity in lots
    strike_selection : str, optional {'equal', 'resilient', 'atm'}
        Mode for finding the strangle, by default 'equal'
    call_strike_offset : float, optional
        Call strike offset in percentage terms, by default 0
    put_strike_offset : float, optional
        Put strike offset in percentage terms, by default 0
    stop_loss : float or string, optional
        Stop loss percentage, by default 'dynamic'
    call_stop_loss : float, optional
        Call stop loss percentage, by default None. If None then stop loss is same as stop_loss.
    put_stop_loss : float, optional
        Put stop loss percentage, by default None. If None then stop loss is same as stop_loss.
    exit_time : tuple, optional
        Exit time, by default (15, 29)
    sleep_time : int, optional
        Sleep time in seconds for updating prices, by default 5
    seconds_to_avg : int, optional
        Seconds to average prices over, by default 30
    simulation_safe_guard : float, optional
        The multiple over the simulated price that will reject stop loss, by default 1.15
    catch_trend : bool, optional
        Catch trend or not, by default False
    trend_qty_ratio : int, optional
        Ratio of trend quantity to strangle quantity, by default 1
    trend_strike_offset : float, optional
        Strike offset for trend order in percentage terms, by default 0
    trend_sl : float, optional
        Stop loss for trend order, by default 0.003
    trend_sl_on_option : bool, optional
        Place stop loss on option, by default 1.75.
    disparity_threshold : float, optional
        Disparity threshold for equality of strikes, by default np.inf
    place_sl_orders : bool, optional
        Place stop loss orders or not, by default False
    move_sl_to_cost : bool, optional
        Move other stop loss to cost or not, by default False
    place_orders_on_sl : bool, optional
        Place orders on stop loss or not, by default False
    convert_to_butterfly : bool, optional
        Convert to butterfly or not, by default False
    conversion_method : str, optional
        Conversion method for butterfly, by default 'breakeven'
    conversion_threshold_pct : float, optional
        Conversion threshold for butterfly if conversion method is 'pct', by default 0.175
    take_profit : float, optional
        Take profit percentage, by default 0
    shared_data : SharedData class, optional
        shared data about client level orderbook and positions, by default None
    notification_url : str, optional
        URL for sending notifications, by default None
    strategy_tag : str, optional
        Strategy tag for logging, by default 'Intraday strangle'
    """

    @log_error(notify=True, raise_error=True)
    @increase_robustness
    def position_monitor(info_dict):
        c_avg_price = info_dict["call_avg_price"]
        p_avg_price = info_dict["put_avg_price"]
        traded_strangle = info_dict["traded_strangle"]

        # EMA parameters
        periods = max(int(seconds_to_avg / sleep_time), 1) if sleep_time >= 1 else 1
        alpha = 2 / (periods + 1)
        ema_values = {
            "call": None,
            "put": None,
            "underlying": None,
        }

        # Conversion to butterfly
        ctb_notification_sent = False
        ctb_message = ""
        ctb_hedge = None
        conversion_threshold_break_even = None

        def process_ctb(
            h_strangle: Strangle,
            method: str,
            threshold_break_even: float,
            threshold_pct: float,
            total_price: float,
        ) -> bool:
            hedge_total_ltp = h_strangle.fetch_total_ltp()

            if method == "breakeven":
                hedge_profit = total_price - hedge_total_ltp - underlying.base
                return hedge_profit >= threshold_break_even

            elif method == "pct":
                if (
                    total_price - (hedge_total_ltp + underlying.base)
                    < threshold_break_even
                ):
                    return False  # Ensuring that this is better than break even method
                return hedge_total_ltp <= total_price * threshold_pct

            else:
                raise ValueError(
                    f"Invalid conversion method: {method}. Valid methods are 'breakeven' and 'pct'."
                )

        if convert_to_butterfly:
            ctb_call_strike = traded_strangle.call_strike + underlying.base
            ctb_put_strike = traded_strangle.put_strike - underlying.base
            ctb_hedge = Strangle(
                ctb_call_strike, ctb_put_strike, underlying.name, expiry
            )
            c_sl = call_stop_loss if call_stop_loss is not None else stop_loss
            p_sl = put_stop_loss if put_stop_loss is not None else stop_loss
            profit_if_call_sl = p_avg_price - (c_avg_price * (c_sl - 1))
            profit_if_put_sl = c_avg_price - (p_avg_price * (p_sl - 1))

            conversion_threshold_break_even = max(profit_if_call_sl, profit_if_put_sl)

        threshold_points = (
            (take_profit * (c_avg_price + p_avg_price)) if take_profit > 0 else np.inf
        )

        last_print_time = current_time()
        last_log_time = current_time()
        last_notify_time = current_time()
        print_interval = timedelta(seconds=10)
        log_interval = timedelta(minutes=25)
        notify_interval = timedelta(minutes=180)

        while not info_dict["trade_complete"]:
            # Fetching prices
            spot_price = underlying.fetch_ltp()
            c_ltp, p_ltp = traded_strangle.fetch_ltp()
            info_dict["underlying_ltp"] = spot_price
            info_dict["call_ltp"] = c_ltp
            info_dict["put_ltp"] = p_ltp

            # Calculate EMA for each series
            for series, price in zip(
                ["call", "put", "underlying"], [c_ltp, p_ltp, spot_price]
            ):
                ema_values[series] = calculate_ema(price, ema_values[series], alpha)

            c_ltp_avg = ema_values["call"]
            p_ltp_avg = ema_values["put"]
            spot_price_avg = ema_values["underlying"]

            info_dict["call_ltp_avg"] = c_ltp_avg
            info_dict["put_ltp_avg"] = p_ltp_avg
            info_dict["underlying_ltp_avg"] = spot_price_avg

            # Calculate IV
            call_iv, put_iv, avg_iv = calculate_strangle_iv(
                call_price=c_ltp,
                put_price=p_ltp,
                call_strike=traded_strangle.call_strike,
                put_strike=traded_strangle.put_strike,
                spot=spot_price,
                time_left=time_to_expiry(expiry),
            )
            info_dict["call_iv"] = call_iv
            info_dict["put_iv"] = put_iv
            info_dict["avg_iv"] = avg_iv

            # Calculate mtm price
            call_exit_price = info_dict.get("call_exit_price", c_ltp)
            put_exit_price = info_dict.get("put_exit_price", p_ltp)
            mtm_price = call_exit_price + put_exit_price

            # Calculate profit
            profit_in_pts = (c_avg_price + p_avg_price) - mtm_price
            profit_in_rs = profit_in_pts * underlying.lot_size * quantity_in_lots
            info_dict["profit_in_pts"] = profit_in_pts
            info_dict["profit_in_rs"] = profit_in_rs

            if take_profit > 0:
                if profit_in_pts >= threshold_points:
                    info_dict["exit_triggers"].update({"take_profit": True})
                    notifier(
                        f"{underlying.name} Take profit triggered with profit of {profit_in_pts} points",
                        notification_url,
                        "INFO",
                    )

            # Conversion to butterfly working
            if (
                not (info_dict["call_sl"] or info_dict["put_sl"])
                and info_dict["time_left_day_start"] * 365 < 1
                and convert_to_butterfly
                and not ctb_notification_sent
                and current_time().time() < time(14, 15)
            ):
                try:
                    ctb_trigger = process_ctb(
                        ctb_hedge,
                        conversion_method,
                        conversion_threshold_break_even,
                        conversion_threshold_pct,
                        info_dict["total_avg_price"],
                    )
                    if ctb_trigger:
                        notifier(
                            f"{underlying.name} Convert to butterfly triggered\n",
                            notification_url,
                            "INFO",
                        )
                        info_dict["exit_triggers"].update(
                            {"convert_to_butterfly": True}
                        )
                        ctb_message = f"Hedged with: {ctb_hedge}\n"
                        info_dict["ctb_hedge"] = ctb_hedge
                        ctb_notification_sent = True
                except Exception as _e:
                    logger.error(f"Error in process_ctb: {_e}")

            message = (
                f"\nUnderlying: {underlying.name}\n"
                f"Time: {current_time() :%d-%m-%Y %H:%M:%S}\n"
                f"Underlying LTP: {spot_price}\n"
                f"Call Strike: {traded_strangle.call_strike}\n"
                f"Put Strike: {traded_strangle.put_strike}\n"
                f"Call Price: {c_ltp}\n"
                f"Put Price: {p_ltp}\n"
                f"MTM Price: {mtm_price}\n"
                f"Call last n avg: {c_ltp_avg}\n"
                f"Put last n avg: {p_ltp_avg}\n"
                f"IVs: {call_iv}, {put_iv}, {avg_iv}\n"
                f"Call SL: {info_dict['call_sl']}\n"
                f"Put SL: {info_dict['put_sl']}\n"
                f"Profit Pts: {info_dict['profit_in_pts']:.2f}\n"
                f"Profit: {info_dict['profit_in_rs']:.2f}\n" + ctb_message
            )
            if current_time() - last_print_time > print_interval:
                print(message)
                last_print_time = current_time()
            if current_time() - last_log_time > log_interval:
                logger.info(message)
                last_log_time = current_time()
            if current_time() - last_notify_time > notify_interval:
                notifier(message, notification_url, "INFO")
                last_notify_time = current_time()
            sleep(sleep_time)

    @log_error(raise_error=True, notify=True)
    @increase_robustness
    def trend_catcher(info_dict, sl_type, qty_ratio, sl, strike_offset):
        offset = 1 - strike_offset if sl_type == "call" else 1 + strike_offset

        spot_price = info_dict["underlying_ltp"]

        # Setting up the trend option
        strike = spot_price * offset
        strike = find_strike(strike, underlying.base)
        opt_type = OptionType.PUT if sl_type == "call" else OptionType.CALL
        qty_in_lots = max(int(quantity_in_lots * qty_ratio), 1)
        trend_option = Option(strike, opt_type, underlying.name, expiry)

        # Placing the trend option order
        sell_avg_price = place_option_order_and_notify(
            trend_option,
            "SELL",
            qty_in_lots,
            "LIMIT",
            "Intraday Strangle Trend Catcher",
            notification_url,
        )

        # Setting up the stop losses on underlying and trend option

        # Underlying stop loss
        sl_multiplier = 1 - sl if sl_type == "call" else 1 + sl
        underlying_sl_price = spot_price * sl_multiplier

        # Trend option stop loss
        option_sl_price = sell_avg_price * trend_sl_on_option

        trend_sl_hit = False
        notifier(
            f"{underlying.name} strangle {sl_type} trend catcher starting. "
            f"Placed {qty_in_lots} lots of {strike} {opt_type.value} at {sell_avg_price}. "
            f"Stoploss prices: {underlying_sl_price, option_sl_price}. "
            f"Underlying Price: {spot_price}",
            notification_url,
            "INFO",
        )

        last_print_time = current_time()
        print_interval = timedelta(seconds=10)
        while all(
            [
                current_time().time() < time(*exit_time),
                not info_dict["trade_complete"],
            ]
        ):
            spot_price = info_dict["underlying_ltp"]
            spot_price_avg = info_dict["underlying_ltp_avg"]
            option_price = trend_option.fetch_ltp()
            trend_sl_hit = (option_price > option_sl_price) and (
                spot_price_avg < underlying_sl_price
                if sl_type == "call"
                else spot_price_avg > underlying_sl_price
            )
            if trend_sl_hit:
                break
            sleep(sleep_time)
            if current_time() - last_print_time > print_interval:
                last_print_time = current_time()
                logger.info(
                    f"{underlying.name} {sl_type} trend catcher running\n"
                    f"Stoploss prices: {underlying_sl_price, option_sl_price}\n"
                    f"Underlying price: {spot_price}\n"
                    f"Underlying price avg: {spot_price_avg}, Stoploss hit: {trend_sl_hit}\n"
                )

        if trend_sl_hit:
            notifier(
                f"{underlying.name} strangle {sl_type} trend catcher stoploss hit.",
                notification_url,
                "INFO",
            )
            square_off = True
        else:
            notifier(
                f"{underlying.name} strangle {sl_type} trend catcher exiting.",
                notification_url,
                "INFO",
            )
            if info_dict["time_left_day_start"] * 365 < 1:  # expiry day
                square_off = False
            else:
                square_off = True

        if square_off:
            # Buying the trend option back
            square_up_avg_price = place_option_order_and_notify(
                trend_option,
                "BUY",
                qty_in_lots,
                "LIMIT",
                "Intraday Strangle Trend Catcher",
                notification_url,
            )
        else:
            square_up_avg_price = trend_option.fetch_ltp()

        points_captured = sell_avg_price - square_up_avg_price
        info_dict["trend_catcher_points_captured"] = points_captured

    def justify_stop_loss(info_dict, side):
        entry_spot = info_dict.get("spot_at_entry")
        current_spot = info_dict.get("underlying_ltp")
        stop_loss_price = info_dict.get(f"{side}_stop_loss_price")

        time_left_day_start = info_dict.get("time_left_day_start")
        time_left_now = time_to_expiry(expiry)
        time_delta_minutes = (time_left_day_start - time_left_now) * 525600
        time_delta_minutes = int(time_delta_minutes)
        time_delta_minutes = min(
            time_delta_minutes, 300
        )  # Hard coded number. At most 300 minutes and not more.
        try:
            simulated_option_price = simulate_price(
                strike=info_dict.get("traded_strangle").call_strike
                if side == "call"
                else info_dict.get("traded_strangle").put_strike,
                flag=side,
                original_atm_iv=info_dict.get("atm_iv_at_entry"),
                original_spot=entry_spot,
                original_time_to_expiry=time_left_day_start,
                new_spot=current_spot,
                time_delta_minutes=time_delta_minutes,
            )
        except (Exception, IntrinsicValueError) as e:
            error_message = (
                f"Error in justify_stop_loss for {underlying.name} {side} strangle: {e}\n"
                f"Setting stop loss to True"
            )
            logger.error(error_message)
            notifier(error_message, notification_url, "ERROR")
            return True

        actual_price = info_dict.get(f"{side}_ltp_avg")
        unjust_increase = (
            actual_price / simulated_option_price > simulation_safe_guard
            and simulated_option_price < stop_loss_price
        )
        if unjust_increase:
            if not info_dict.get(f"{side}_sl_check_notification_sent"):
                message = (
                    f"{underlying.name} strangle {side} stop loss appears to be unjustified. "
                    f"Actual price: {actual_price}, Simulated price: {simulated_option_price}"
                )
                notifier(message, notification_url, "CRUCIAL")
                info_dict[f"{side}_sl_check_notification_sent"] = True

            # Additional check for unjustified stop loss (forcing stoploss to trigger even if unjustified only if
            # the price has increased by more than 2 times AND spot has moved by more than 0.5%)
            spot_change = (current_spot / entry_spot) - 1
            spot_moved = (
                spot_change > 0.012 if side == "call" else spot_change < -0.0035
            )  # Hard coded number
            if (
                spot_moved and (actual_price / stop_loss_price) > 1.6
            ):  # Hard coded number
                message = (
                    f"{underlying.name} strangle {side} stop loss forced to trigger due to price increase. "
                    f"Price increase from stop loss price: {actual_price / simulated_option_price}"
                )
                notifier(message, notification_url, "CRUCIAL")
                return True
            else:
                return False
        else:
            message = (
                f"{underlying.name} strangle {side} stop loss triggered. "
                f"Actual price: {actual_price}, Simulated price: {simulated_option_price}"
            )
            notifier(message, notification_url, "CRUCIAL")
            return True

    def check_for_stop_loss(info_dict, side, refresh_orderbook=False):
        """Check for stop loss."""

        stop_loss_order_ids = info_dict.get(f"{side}_stop_loss_order_ids")

        if stop_loss_order_ids is None:  # If stop loss order ids are not provided
            ltp_avg = info_dict.get(f"{side}_ltp_avg", info_dict.get(f"{side}_ltp"))
            stop_loss_price = info_dict.get(f"{side}_stop_loss_price")
            stop_loss_triggered = ltp_avg > stop_loss_price
            if stop_loss_triggered:
                stop_loss_justified = justify_stop_loss(info_dict, side)
                if stop_loss_justified:
                    info_dict[f"{side}_sl"] = True

        else:  # If stop loss order ids are provided
            orderbook = fetch_orderbook_if_needed(
                shared_data, refresh_needed=refresh_orderbook
            )
            if shared_data is None:
                sleep(3)
            orders_triggered, orders_complete = process_stop_loss_order_statuses(
                orderbook,
                stop_loss_order_ids,
                context=side,
                notify_url=notification_url,
            )
            if orders_triggered:
                justify_stop_loss(info_dict, side)
                info_dict[f"{side}_sl"] = True
                if not orders_complete:
                    info_dict[f"{side}_stop_loss_order_ids"] = None

    def process_stop_loss(info_dict, sl_type):
        if (
            info_dict["call_sl"] and info_dict["put_sl"]
        ):  # Check to avoid double processing
            return

        traded_strangle = info_dict["traded_strangle"]
        other_side: str = "call" if sl_type == "put" else "put"

        # Buying the stop loss option back if it is not already bought
        if info_dict[f"{sl_type}_stop_loss_order_ids"] is None:
            option_to_buy = (
                traded_strangle.call_option
                if sl_type == "call"
                else traded_strangle.put_option
            )
            exit_price = place_option_order_and_notify(
                option_to_buy,
                "BUY",
                quantity_in_lots,
                "LIMIT",
                strategy_tag,
                notification_url,
            )
        else:
            orderbook = fetch_book("orderbook")
            exit_price = (
                lookup_and_return(
                    orderbook,
                    "orderid",
                    info_dict[f"{sl_type}_stop_loss_order_ids"],
                    "averageprice",
                )
                .astype(float)
                .mean()
            )
        info_dict[f"{sl_type}_exit_price"] = exit_price

        if move_sl_to_cost:
            info_dict[f"{other_side}_stop_loss_price"] = info_dict[
                f"{other_side}_avg_price"
            ]
            if (
                info_dict[f"{other_side}_stop_loss_order_ids"] is not None
                or place_orders_on_sl
            ):
                if info_dict[f"{other_side}_stop_loss_order_ids"] is not None:
                    cancel_pending_orders(
                        info_dict[f"{other_side}_stop_loss_order_ids"], "STOPLOSS"
                    )
                option_to_repair = (
                    traded_strangle.call_option
                    if other_side == "call"
                    else traded_strangle.put_option
                )
                info_dict[
                    f"{other_side}_stop_loss_order_ids"
                ] = place_option_order_and_notify(
                    instrument=option_to_repair,
                    action="BUY",
                    qty_in_lots=quantity_in_lots,
                    prices=info_dict[f"{other_side}_stop_loss_price"],
                    order_tag=f"{other_side.capitalize()} SL move to cost",
                    webhook_url=notification_url,
                    stop_loss_order=True,
                    target_status="trigger pending",
                    return_avg_price=False,
                )

        # Starting the trend catcher
        if catch_trend:
            trend_thread = Thread(
                target=trend_catcher,
                args=(
                    info_dict,
                    sl_type,
                    trend_qty_ratio,
                    trend_sl,
                    trend_strike_offset,
                ),
                name=f"{underlying.name} {sl_type} trend catcher",
            )
            trend_thread.start()
            info_dict["active_threads"].append(trend_thread)

        refresh_orderbook = True
        # Wait for exit or other stop loss to hit
        while all(
            [
                current_time().time() < time(*exit_time),
                not info_dict["exit_triggers"]["take_profit"],
            ]
        ):
            check_for_stop_loss(
                info_dict, other_side, refresh_orderbook=refresh_orderbook
            )
            if info_dict[f"{other_side}_sl"]:
                if info_dict[f"{other_side}_stop_loss_order_ids"] is None:
                    other_sl_option = (
                        traded_strangle.call_option
                        if other_side == "call"
                        else traded_strangle.put_option
                    )
                    notifier(
                        f"{underlying.name} strangle {other_side} stop loss hit.",
                        notification_url,
                        "CRUCIAL",
                    )
                    other_exit_price = place_option_order_and_notify(
                        other_sl_option,
                        "BUY",
                        quantity_in_lots,
                        "LIMIT",
                        strategy_tag,
                        notification_url,
                    )
                else:
                    orderbook = fetch_book("orderbook")
                    other_exit_price = (
                        lookup_and_return(
                            orderbook,
                            "orderid",
                            info_dict[f"{other_side}_stop_loss_order_ids"],
                            "averageprice",
                        )
                        .astype(float)
                        .mean()
                    )
                info_dict[f"{other_side}_exit_price"] = other_exit_price
                break
            refresh_orderbook = False
            sleep(1)

    # Entering the main function
    expiry = underlying.current_expiry

    # Setting stop loss
    stop_loss_dict = {
        "fixed": {"BANKNIFTY": 1.7, "NIFTY": 1.5},
        "dynamic": {"BANKNIFTY": 1.7, "NIFTY": 1.5},
    }

    if isinstance(stop_loss, str):
        if stop_loss == "dynamic" and time_to_expiry(expiry, in_days=True) < 1:
            stop_loss = 1.7
        else:
            stop_loss = stop_loss_dict[stop_loss].get(underlying.name, 1.6)
    else:
        stop_loss = stop_loss

    if strike_selection == "equal":
        strangle = most_equal_strangle(
            underlying=underlying,
            call_strike_offset=call_strike_offset,
            put_strike_offset=put_strike_offset,
            disparity_threshold=disparity_threshold,
            exit_time=exit_time,
            expiry=expiry,
            notification_url=notification_url,
        )
        if strangle is None:
            notifier(
                f"{underlying.name} no strangle found within disparity threshold {disparity_threshold}",
                notification_url,
                "INFO",
            )
            return
    elif strike_selection == "resilient":
        strangle = underlying.most_resilient_strangle(
            stop_loss=stop_loss, expiry=expiry
        )
    elif strike_selection == "atm":
        atm_strike = find_strike(underlying.fetch_ltp(), underlying.base)
        strangle = Strangle(atm_strike, atm_strike, underlying.name, expiry)
    else:
        raise ValueError(f"Invalid find mode: {strike_selection}")

    call_ltp, put_ltp = strangle.fetch_ltp()

    # Placing the main order
    call_avg_price, put_avg_price = place_option_order_and_notify(
        strangle,
        "SELL",
        quantity_in_lots,
        "LIMIT",
        strategy_tag,
        notification_url,
        return_avg_price=True,
    )
    total_avg_price = call_avg_price + put_avg_price

    call_stop_loss_price = (
        call_avg_price * call_stop_loss
        if call_stop_loss
        else call_avg_price * stop_loss
    )
    put_stop_loss_price = (
        put_avg_price * put_stop_loss if put_stop_loss else put_avg_price * stop_loss
    )

    underlying_ltp = underlying.fetch_ltp()

    # Logging information and sending notification
    trade_log = {
        "Time": current_time().strftime("%d-%m-%Y %H:%M:%S"),
        "Index": underlying.name,
        "Underlying price": underlying_ltp,
        "Call strike": strangle.call_strike,
        "Put strike": strangle.put_strike,
        "Expiry": expiry,
        "Action": "SELL",
        "Call price": call_avg_price,
        "Put price": put_avg_price,
        "Total price": total_avg_price,
        "Order tag": strategy_tag,
    }

    summary_message = "\n".join(f"{k}: {v}" for k, v in trade_log.items())

    # Setting the IV information at entry

    traded_call_iv, traded_put_iv, traded_avg_iv = calculate_strangle_iv(
        call_price=call_avg_price,
        put_price=put_avg_price,
        call_strike=strangle.call_strike,
        put_strike=strangle.put_strike,
        spot=underlying_ltp,
        time_left=time_to_expiry(expiry),
    )
    try:
        atm_iv_at_entry = underlying.fetch_atm_info()["avg_iv"]
    except Exception as e:
        logger.error(f"Error in fetching ATM IV: {e}")
        atm_iv_at_entry = np.nan
    time_left_at_trade = time_to_expiry(expiry)

    # Sending the summary message
    summary_message += (
        f"\nTraded IVs: {traded_call_iv}, {traded_put_iv}, {traded_avg_iv}\n"
        f"ATM IV at entry: {atm_iv_at_entry}\n"
        f"Call SL: {call_stop_loss_price}, Put SL: {put_stop_loss_price}"
    )
    notifier(summary_message, notification_url, "INFO")

    if place_sl_orders:
        call_stop_loss_order_ids = place_option_order_and_notify(
            instrument=strangle.call_option,
            action="BUY",
            qty_in_lots=quantity_in_lots,
            prices=call_stop_loss_price,
            order_tag="Call SL Strangle",
            webhook_url=notification_url,
            stop_loss_order=True,
            target_status="trigger pending",
            return_avg_price=False,
        )
        put_stop_loss_order_ids = place_option_order_and_notify(
            instrument=strangle.put_option,
            action="BUY",
            qty_in_lots=quantity_in_lots,
            prices=put_stop_loss_price,
            order_tag="Put SL Strangle",
            webhook_url=notification_url,
            stop_loss_order=True,
            target_status="trigger pending",
            return_avg_price=False,
        )
    else:
        call_stop_loss_order_ids = None
        put_stop_loss_order_ids = None

    # Setting up shared info dict
    shared_info_dict = {
        "traded_strangle": strangle,
        "spot_at_entry": underlying_ltp,
        "call_avg_price": call_avg_price,
        "put_avg_price": put_avg_price,
        "total_avg_price": total_avg_price,
        "atm_iv_at_entry": atm_iv_at_entry,
        "call_stop_loss_price": call_stop_loss_price,
        "put_stop_loss_price": put_stop_loss_price,
        "call_stop_loss_order_ids": call_stop_loss_order_ids,
        "put_stop_loss_order_ids": put_stop_loss_order_ids,
        "time_left_day_start": time_left_at_trade,
        "call_ltp": call_ltp,
        "put_ltp": put_ltp,
        "underlying_ltp": underlying_ltp,
        "call_iv": traded_call_iv,
        "put_iv": traded_put_iv,
        "avg_iv": traded_avg_iv,
        "call_sl": False,
        "put_sl": False,
        "exit_triggers": {"convert_to_butterfly": False, "take_profit": False},
        "trade_complete": False,
        "call_sl_check_notification_sent": False,
        "put_sl_check_notification_sent": False,
        "active_threads": [],
        "trend_catcher_points_captured": 0,
    }

    position_monitor_thread = Thread(
        target=position_monitor, args=(shared_info_dict,), name="Position monitor"
    )
    position_monitor_thread.start()
    shared_info_dict["active_threads"].append(position_monitor_thread)
    sleep(3)  # To ensure that the position monitor thread has started

    refresh_book = True

    # Wait for exit time or both stop losses to hit (Main Loop)
    while all(
        [
            current_time().time() < time(*exit_time),
            not any(shared_info_dict["exit_triggers"].values()),
        ]
    ):
        check_for_stop_loss(shared_info_dict, "call", refresh_orderbook=refresh_book)
        if shared_info_dict["call_sl"]:
            process_stop_loss(shared_info_dict, "call")
            break
        check_for_stop_loss(shared_info_dict, "put")
        if shared_info_dict["put_sl"]:
            process_stop_loss(shared_info_dict, "put")
            break
        refresh_book = False
        sleep(1)

    # Out of the while loop, so exit time reached or both stop losses hit, or we are hedged

    # If we are hedged then wait till exit time
    # noinspection PyTypeChecker
    if shared_info_dict["exit_triggers"]["convert_to_butterfly"]:
        hedge_strangle = shared_info_dict["ctb_hedge"]
        place_option_order_and_notify(
            hedge_strangle,
            "BUY",
            quantity_in_lots,
            "LIMIT",
            strategy_tag,
            notification_url,
            return_avg_price=False,
        )
        if place_sl_orders:
            cancel_pending_orders(
                shared_info_dict["call_stop_loss_order_ids"]
                + shared_info_dict["put_stop_loss_order_ids"]
            )
        notifier(f"{underlying.name}: Converted to butterfly", notification_url, "INFO")
        while current_time().time() < time(*exit_time):
            sleep(3)

    call_sl = shared_info_dict["call_sl"]
    put_sl = shared_info_dict["put_sl"]

    if not call_sl and not put_sl:  # Both stop losses not hit
        call_exit_avg_price, put_exit_avg_price = place_option_order_and_notify(
            strangle,
            "BUY",
            quantity_in_lots,
            "LIMIT",
            strategy_tag,
            notification_url,
            return_avg_price=True,
            square_off_order=True,
        )
        # noinspection PyTypeChecker
        if (
            place_sl_orders
            and not shared_info_dict["exit_triggers"]["convert_to_butterfly"]
        ):
            cancel_pending_orders(
                shared_info_dict["call_stop_loss_order_ids"]
                + shared_info_dict["put_stop_loss_order_ids"]
            )
        shared_info_dict["call_exit_price"] = call_exit_avg_price
        shared_info_dict["put_exit_price"] = put_exit_avg_price

    elif (call_sl or put_sl) and not (call_sl and put_sl):  # Only one stop loss hit
        exit_option_type: str = "put" if call_sl else "call"
        exit_option = strangle.put_option if call_sl else strangle.call_option
        non_sl_exit_price = place_option_order_and_notify(
            exit_option,
            "BUY",
            quantity_in_lots,
            "LIMIT",
            strategy_tag,
            notification_url,
            square_off_order=True,
        )
        if place_sl_orders or place_orders_on_sl:
            cancel_pending_orders(
                shared_info_dict[f"{exit_option_type}_stop_loss_order_ids"]
            )
        shared_info_dict[f"{exit_option_type}_exit_price"] = non_sl_exit_price

    else:  # Both stop losses hit
        pass

    shared_info_dict["trade_complete"] = True
    for thread in shared_info_dict["active_threads"]:
        thread.join()

    # Calculate profit
    total_exit_price = (
        shared_info_dict["call_exit_price"] + shared_info_dict["put_exit_price"]
    )
    # Exit message
    exit_message = (
        f"{underlying.name} strangle exited.\n"
        f"Time: {current_time() :%d-%m-%Y %H:%M:%S}\n"
        f"Underlying LTP: {shared_info_dict['underlying_ltp']}\n"
        f"Call Price: {shared_info_dict['call_ltp']}\n"
        f"Put Price: {shared_info_dict['put_ltp']}\n"
        f"Call SL: {shared_info_dict['call_sl']}\n"
        f"Put SL: {shared_info_dict['put_sl']}\n"
        f"Call Exit Price: {shared_info_dict['call_exit_price']}\n"
        f"Put Exit Price: {shared_info_dict['put_exit_price']}\n"
        f"Total Exit Price: {total_exit_price}\n"
        f"Total Entry Price: {total_avg_price}\n"
        f"Profit Points: {total_avg_price - total_exit_price}\n"
        f"Chase Points: {shared_info_dict['trend_catcher_points_captured']}\n"
    )
    # Exit dict
    exit_dict = {
        "Call exit price": shared_info_dict["call_exit_price"],
        "Put exit price": shared_info_dict["put_exit_price"],
        "Total exit price": total_exit_price,
        "Points captured": total_avg_price - total_exit_price,
        "Call stop loss": shared_info_dict["call_sl"],
        "Put stop loss": shared_info_dict["put_sl"],
        "Trend catcher points": shared_info_dict["trend_catcher_points_captured"],
    }

    notifier(exit_message, notification_url, "CRUCIAL")
    trade_log.update(exit_dict)
    underlying.strategy_log[strategy_tag].append(trade_log)

    return shared_info_dict


@exit_on_error
@increase_robustness
def intraday_trend(
    underlying: Index | Stock,
    quantity_in_lots: int,
    exit_time: tuple[int, int] = (15, 27),
    threshold_movement: Optional[float] = None,
    beta: Optional[float] = 0.8,
    stop_loss: Optional[float] = 0.003,
    max_entries: Optional[int] = 3,
    hedge_offset: Optional[float | bool] = 0.004,
    notification_url: Optional[str] = None,
    strategy_tag: Optional[str] = "Intraday trend",
):
    def get_futures_basis(traded_price):
        try:
            underlying.set_future_symbol_tokens()
            fut_1_price, fut_2_price = underlying.fetch_ltp(
                future=0
            ), underlying.fetch_ltp(future=1)
        except Exception as e:
            logger.error(f"Error in getting futures prices: {e}")
            notifier(f"Error in getting futures prices: {e}", notification_url, "INFO")
            fut_1_price, fut_2_price = np.nan, np.nan
        spot_price = underlying.fetch_ltp()
        b1 = traded_price - spot_price
        b2 = fut_1_price - spot_price
        b3 = fut_2_price - fut_1_price
        return b1, b2, b3

    def execute_hedge_leg(action: Action) -> float:
        # execute_hedge and hedge_instrument are referred to in the nonlocal scope
        if execute_hedge:
            _avg_price = place_option_order_and_notify(
                hedge_instrument,
                action,
                quantity_in_lots,
                "LIMIT",
                strategy_tag + " hedge",
                notification_url,
                return_avg_price=True,
            )
        else:
            _avg_price = np.nan
        return _avg_price

    if current_time().time() > time(9, 18):
        try:
            open_time = current_time().replace(hour=9, minute=16, second=0)
            open_price_data = fetch_historical_prices(
                underlying.token, "ONE_MINUTE", open_time, open_time
            )
            open_price = open_price_data[0][1]
        except Exception as e:
            notifier(
                f"Error in fetching historical prices: {e}", notification_url, "INFO"
            )
            open_price = underlying.fetch_ltp()
    else:
        while current_time().time() < time(9, 16):
            sleep(1)
        open_price = underlying.fetch_ltp()

    threshold_movement = threshold_movement or (IndiaVix.fetch_ltp() * (beta or 1)) / 48

    exit_time_object = time(*exit_time)
    scan_end_time = (
        datetime.combine(current_time().date(), exit_time_object)
        - timedelta(minutes=10)
    ).time()
    price_boundaries = [
        open_price * (1 + ((-1) ** i) * threshold_movement / 100) for i in range(2)
    ]

    # Hedge flag
    execute_hedge = False if hedge_offset is False else True

    notifier(
        f"{underlying.name} trender starting with {threshold_movement:0.2f} threshold movement\n"
        f"Current Price: {open_price}\nUpper limit: {price_boundaries[0]:0.2f}\n"
        f"Lower limit: {price_boundaries[1]:0.2f}.",
        notification_url,
        "INFO",
    )

    entries = 0
    movement = 0
    entries_log = []
    while entries < max_entries and current_time().time() < exit_time_object:
        # Scan for entry condition
        notifier(
            f"{underlying.name} trender {entries+1} scanning for entry condition.",
            notification_url,
            "INFO",
        )
        while current_time().time() < scan_end_time:
            ltp = underlying.fetch_ltp()
            movement = (ltp - open_price) / open_price * 100
            if abs(movement) > threshold_movement:
                break
            sleep_until_next_action(1, exit_time)

        if current_time().time() > scan_end_time:
            notifier(
                f"{underlying.name} trender {entries+1} exiting due to time.",
                notification_url,
                "CRUCIAL",
            )
            break

        # Entry condition met taking position
        price = underlying.fetch_ltp()
        atm_strike = find_strike(price, underlying.base)
        position: Action = Action.BUY if movement > 0 else Action.SELL

        # Main instrument
        atm_synthetic_fut = SyntheticFuture(
            atm_strike, underlying.name, underlying.current_expiry
        )
        # Hedge instrument
        if execute_hedge:
            hedge_strike_multiplier = (
                1 + hedge_offset if position == Action.BUY else 1 - hedge_offset
            )
            hedge_strike = find_strike(price * hedge_strike_multiplier, underlying.base)
            hedge_option_type: OptionType = (
                OptionType.CALL if position == Action.BUY else OptionType.PUT
            )
            hedge_instrument = Option(
                strike=hedge_strike,
                option_type=hedge_option_type,
                underlying=underlying.name,
                expiry=underlying.current_expiry,
            )
        else:
            hedge_strike = np.nan
            hedge_instrument = None

        stop_loss_price = price * (
            (1 - stop_loss) if position == Action.BUY else (1 + stop_loss)
        )
        stop_loss_hit = False
        notifier(
            f"{underlying.name} {position} trender triggered with {movement:0.2f} movement. "
            f"{underlying.name} at {price}. "
            f"Stop loss at {stop_loss_price}.",
            notification_url,
            "INFO",
        )

        # Main order
        call_entry_price, put_entry_price = place_option_order_and_notify(
            atm_synthetic_fut,
            position,
            quantity_in_lots,
            "LIMIT",
            strategy_tag,
            notification_url,
            return_avg_price=True,
        )

        # Hedge order
        hedge_entry_price = execute_hedge_leg(Action.SELL)

        # Spot-Future basis calculation
        entry_price = atm_strike + call_entry_price - put_entry_price
        traded_basis, spot_future_basis, arbitrage_basis = get_futures_basis(
            entry_price
        )

        notifier(
            f"{underlying.name} trender {entries+1} entry price: {entry_price} "
            f"Hedge order strike: {hedge_strike}, Hedge order price: {hedge_entry_price}",
            notification_url,
            "CRUCIAL",
        )

        trade_info = {
            "Entry time": current_time().strftime("%d-%m-%Y %H:%M:%S"),
            "Position": position,
            "Spot price": price,
            "Entry price": entry_price,
            "Hedge order strike": hedge_strike,
            "Hedge order price": hedge_entry_price,
            "Stop loss": stop_loss_price,
            "Threshold movement": threshold_movement,
            "Movement": movement,
            "Entry Basis": (traded_basis, spot_future_basis, arbitrage_basis),
        }

        # Tracking position
        while current_time().time() < exit_time_object:
            ltp = underlying.fetch_ltp()
            movement = (ltp - open_price) / open_price * 100
            stop_loss_hit = (
                (ltp < stop_loss_price)
                if position == Action.BUY
                else (ltp > stop_loss_price)
            )
            if stop_loss_hit:
                break
            sleep_until_next_action(1, exit_time)

        # Exit condition met exiting position (stop loss or time)
        price = underlying.fetch_ltp()
        stop_loss_message = f"Trender stop loss hit. " if stop_loss_hit else ""
        notifier(
            f"{stop_loss_message}{underlying.name} trender {entries+1} exiting.",
            notification_url,
            "CRUCIAL",
        )
        # Main exit order
        call_exit_price, put_exit_price = place_option_order_and_notify(
            atm_synthetic_fut,
            "BUY" if position == Action.SELL else "SELL",
            quantity_in_lots,
            "LIMIT",
            strategy_tag,
            notification_url,
            square_off_order=True,
        )

        # Hedge exit order
        hedge_exit_price = execute_hedge_leg(Action.BUY)

        exit_price = atm_strike + call_exit_price - put_exit_price
        hedge_pnl = hedge_entry_price - hedge_exit_price
        pnl = (
            (exit_price - entry_price)
            if position == Action.BUY
            else (entry_price - exit_price)
        ) + hedge_pnl
        pnl_pct = pnl / entry_price * 100

        traded_basis, spot_future_basis, arbitrage_basis = get_futures_basis(exit_price)

        trade_info.update(
            {
                "Exit time": current_time().strftime("%d-%m-%Y %H:%M:%S"),
                "Stop loss hit": stop_loss_hit,
                "Spot exit price": price,
                "Exit price": exit_price,
                "Hedge exit price": hedge_exit_price,
                "Hedge PnL": hedge_pnl,
                "Exit basis": (traded_basis, spot_future_basis, arbitrage_basis),
                "Basis changes": None,  # To be filled later
                "PnL": pnl,
                "PnL Pct": pnl_pct,
            }
        )

        # Spot-Future basis calculation
        basis_changes = [
            exit_basis - entry_basis
            for exit_basis, entry_basis in zip(
                trade_info["Exit basis"], trade_info["Entry Basis"]
            )
        ]
        # Basis is favourable if it increases for long and decreases for short
        basis_changes = [
            basis_change if position == Action.BUY else -basis_change
            for basis_change in basis_changes
        ]
        trade_info["Basis changes"] = basis_changes
        traded_basis_change = basis_changes[0]
        notifier(
            f"{underlying.name} trender {entries+1} exit price: {exit_price}, PNL Pct: {pnl_pct:0.2f}, "
            f"Traded basis change: {traded_basis_change}, Hedge Points: {hedge_pnl}",
            notification_url,
            "CRUCIAL",
        )
        entries_log.append(trade_info)
        entries += 1

    combined_pnl_pct = (
        sum(entry["PnL Pct"] for entry in entries_log) if entries_log else 0
    )
    notifier(
        f"{underlying.name} trender completed. Total PnL Pct: {combined_pnl_pct:0.2f}",
        notification_url,
        "CRUCIAL",
    )
    underlying.strategy_log[strategy_tag].extend(entries_log)
