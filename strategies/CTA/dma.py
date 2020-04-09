from rqalpha.api import *
import talib
from strategies.utils import *


def init(context):
    data.init_rqdata()
    # context.pool = ['RB', 'TA', 'P', 'RU', 'ZN', 'CU', 'CF']
    context.pool = ['RB']

    context.rolling_future = []
    context.futures = {}
    context.rolling_future = [rqdatac.futures.get_dominant(x, context.now)[context.now.strftime('%Y-%m-%d')] for x in
                              context.pool]
    for item in context.pool:
        context.futures[item] = int(instruments(item + '888', market='cn').contract_multiplier)
        subscribe(item+'888')

    subscribe(context.rolling_future)
    context.change_signal = False
    # 实时打印日志
    logger.info("RunInfo: {}".format(context.run_info))
    context.SHORTPERIOD = 20
    context.LONGPERIOD = 120

    context.dropdown_value_lv1 = -0.01
    context.dropdown_value_lv2 = -0.03
    context.dropdown_count = 0
    context.start_net_value = context.portfolio.total_value


def before_trading(context):
    # 主力换月
    context.close_symbol = [rqdatac.futures.get_dominant(x, context.now)[context.now.strftime('%Y-%m-%d')] for x in
                           context.pool]
    if context.rolling_future != context.close_symbol:
        context.change_signal = True


def handle_bar(context, bar_dict):
    context.dropdown_count -= 1
    # if touch dropdown
    if stop_loss(context, bar_dict):
        return

    if context.change_signal:
        # print('进入换月函数,新的主力合约为：{}'.format(context.close_symbol))
        change_dominant(context, bar_dict, True)
        context.change_signal = False

    if context.dropdown_count > 0:
        return

    i = 0
    for item in context.rolling_future:
        prices = history_bars(item, context.SHORTPERIOD, '1d', 'close')
        short_avg = talib.SMA(prices, context.SHORTPERIOD)
        long_position = context.portfolio.future_account.positions[context.rolling_future[i]].buy_quantity
        short_position = context.portfolio.future_account.positions[context.rolling_future[i]].sell_quantity
        target_lot = int(int(context.portfolio.total_value) / len(context.futures) /
                         int(context.futures[context.pool[i]]) / int(bar_dict[item].close))
        # logger.info(str(bar_dict[item].close) + ' vs ' + str(short_avg[-1]))

        if long_position == 0 and short_position == 0:
            if bar_dict[item].close < short_avg[-1]:
                sell_open(item, target_lot, style=LimitOrder(bar_dict[item].close))
            else:
                buy_open(item, target_lot, style=LimitOrder(bar_dict[item].close))
        if long_position > 0:
            if bar_dict[item].close < short_avg[-1]:
                sell_close(item, long_position, style=LimitOrder(bar_dict[item].close))
                sell_open(item, target_lot, style=LimitOrder(bar_dict[item].close))
        if short_position > 0:
            if bar_dict[item].close > short_avg[-1]:
                buy_close(item, short_position, style=LimitOrder(bar_dict[item].close))
                buy_open(item, target_lot, style=LimitOrder(bar_dict[item].close))
        i += 1


def stop_loss(context, bar_dict):
    i = 0
    for item in context.rolling_future:
        long_position = context.portfolio.future_account.positions[context.rolling_future[i]].buy_quantity
        short_position = context.portfolio.future_account.positions[context.rolling_future[i]].sell_quantity
        close_change_percent = bar_dict[item].close/bar_dict[item].prev_close - 1
        if (long_position > 0 and (close_change_percent < context.dropdown_value_lv1)) \
                or (short_position > 0 and (close_change_percent > -context.dropdown_value_lv1)):
            if context.change_signal:
                # print('进入换月函数,新的主力合约为：{}'.format(context.close_symbol))
                change_dominant(context, bar_dict, False)
                context.change_signal = False
                if abs(close_change_percent) > abs(context.dropdown_value_lv2):
                    context.dropdown_count = 4
                elif abs(close_change_percent) > abs(context.dropdown_value_lv1):
                    context.dropdown_count = 2
                return True
            if long_position > 0:
                sell_close(item, long_position, style=LimitOrder(bar_dict[item].close))
            if short_position > 0:
                buy_close(item, short_position, style=LimitOrder(bar_dict[item].close))
            i += 1
            if abs(close_change_percent) > abs(context.dropdown_value_lv2):
                context.dropdown_count = 4
            elif abs(close_change_percent) > abs(context.dropdown_value_lv1):
                context.dropdown_count = 2
            return True
    return False


def change_dominant(context, bar_dict, fire_rolling):
    s1 = context.close_symbol
    for i in range(0, len(s1)):
        if context.close_symbol[i] != context.rolling_future[i]:
            print('换月合约：{}'.format(context.close_symbol[i]))
            if len(context.portfolio.positions) != 0:
                if context.portfolio.positions[context.rolling_future[i]].sell_quantity != 0:
                    long_position = context.portfolio.future_account.positions[context.rolling_future[i]].buy_quantity
                    short_position = context.portfolio.future_account.positions[context.rolling_future[i]].sell_quantity
                    # 平空仓
                    buy_close(context.rolling_future[i], short_position,
                              style=LimitOrder(bar_dict[context.rolling_future[i]].close))
                    # 换仓
                    if fire_rolling:
                        sell_open(context.close_symbol[i], short_position,
                                  style=LimitOrder(bar_dict[context.close_symbol[i]].close))
                elif context.portfolio.positions[context.rolling_future[i]].buy_quantity != 0:
                    long_position = context.portfolio.future_account.positions[context.rolling_future[i]].buy_quantity
                    short_position = context.portfolio.future_account.positions[context.rolling_future[i]].sell_quantity
                    # 平多仓
                    sell_close(context.rolling_future[i], long_position,
                               style=LimitOrder(bar_dict[context.rolling_future[i]].close))
                    # 换仓
                    if fire_rolling:
                        buy_open(context.close_symbol[i], long_position,
                                 style=LimitOrder(bar_dict[context.close_symbol[i]].close))

    unsubscribe(context.rolling_future)
    context.rolling_future = context.close_symbol
    subscribe(context.rolling_future)
