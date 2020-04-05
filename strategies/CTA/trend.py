from rqalpha.api import *
from strategies.utils import *
import copy
import numpy as np


def init(context):
    data.init_rqdata()
    context.pool = ['RB', 'TA', 'P', 'RU', 'ZN', 'CU', 'CF']
    # context.pool = [ 'P']
    # context.pool = ['CU']
    context.rolling_future = [rqdatac.futures.get_dominant(x, context.now)[context.now.strftime('%Y-%m-%d')] for x in
                              context.pool]
    context.futures = {}
    context.short_queue = {}
    context.middle_queue = {}
    context.long_queue = {}
    context.sma_scores = {}
    context.previous_sma_scores = {}
    context.suffix = '888'
    for item in context.pool:
        context.futures[item] = int(instruments(item + context.suffix, market='cn').contract_multiplier)
        context.previous_sma_scores[item] = 0
        context.sma_scores[item] = 0
        context.short_queue[item] = Queue(20)
        context.middle_queue[item] = Queue(40)
        context.long_queue[item] = Queue(60)
        subscribe(item + context.suffix)

    subscribe(context.rolling_future)
    context.window = 60
    context.counter = 0
    context.change_signal = False
    # 实时打印日志
    logger.info("RunInfo: {}".format(context.run_info))


def before_trading(context):
    # 主力换月
    context.last_symbol = [rqdatac.futures.get_dominant(x, context.now)[context.now.strftime('%Y-%m-%d')] for x in context.pool]
    if context.rolling_future != context.last_symbol:
        context.change_signal = True


def handle_bar(context, bar_dict):
    if context.change_signal:
        # print('进入换月函数,新的主力合约为：{}'.format(context.last_symbol))
        change_dominant(context, bar_dict)
        context.change_signal = False
    context.counter += 1
    if (context.counter <= 60):  # donot trade
        prepare_data(context, bar_dict)
        return

    context.previous_sma_scores = copy.deepcopy(context.sma_scores)
    calc_sma_signal(context, bar_dict)
    # logger.info(context.sma_scores)
    handle_sma_signal(context, bar_dict)

    prepare_data(context, bar_dict)


def prepare_data(context, bar_dict):
    for key in context.futures:
        context.short_queue[key].enqueue(bar_dict[key + context.suffix].close)
        context.middle_queue[key].enqueue(bar_dict[key + context.suffix].close)
        context.long_queue[key].enqueue(bar_dict[key + context.suffix].close)


def calc_sma_signal(context, bar_dict):
    for key in context.futures:
        short_score = 1 if bar_dict[key + context.suffix].close > np.mean(context.short_queue[key].tolist()) else -1
        middle_score = 1 if bar_dict[key + context.suffix].close > np.mean(context.middle_queue[key].tolist()) else -1
        long_score = 1 if bar_dict[key + context.suffix].close > np.mean(context.long_queue[key].tolist()) else -1
        context.sma_scores[key] = short_score + middle_score + long_score


def handle_sma_signal(context, bar_dict):  # version 2, consider score weight
    try:

        weight = 3
        total_value = int((context.portfolio.total_value))
        target_notional = int(total_value * weight / len(context.futures))
        i = 0

        for key in context.sma_scores:
            score = context.previous_sma_scores[key] * context.sma_scores[key]
            target_future = context.rolling_future[i]
            lot = int(target_notional / int(context.futures[key]) / int(bar_dict[target_future].last))
            logger.info(key + " ~" + str(score) + " ~" + str(context.sma_scores[key]))
            target_lot = 0
            if lot == 0:
                continue
            if score > 0:  # same direction
                if score == 3:
                    if context.sma_scores[key] == 3:
                        buy_open(target_future, int(lot * 2 / 3), style=LimitOrder(bar_dict[target_future].last))
                    elif context.sma_scores[key] == -3:
                        sell_open(target_future, int(lot * 2 / 3), style=LimitOrder(bar_dict[target_future].last))
                    elif context.sma_scores[key] == -1:
                        buy_close(target_future, int(lot * 2 / 3), style=LimitOrder(bar_dict[target_future].last))
                    else:  # ==1
                        sell_close(target_future, int(lot * 2 / 3), style=LimitOrder(bar_dict[target_future].last))

            elif score == 0:
                if context.sma_scores[key] < 0:
                    sell_open(target_future, abs(int(lot * context.sma_scores[key] / 3)),
                              style=LimitOrder(bar_dict[target_future].last))
                else:
                    buy_open(target_future, abs(int(lot * context.sma_scores[key] / 3)),
                             style=LimitOrder(bar_dict[target_future].last))
            else:
                if context.sma_scores[key] > 0:
                    buy_close(target_future, context.future_account.positions[target_future].sell_quantity,
                              style=LimitOrder(bar_dict[target_future].last))
                    buy_open(target_future, abs(int(lot * context.sma_scores[key] / 3)),
                             style=LimitOrder(bar_dict[target_future].last))
                else:
                    sell_close(target_future, context.future_account.positions[target_future].buy_quantity,
                               style=LimitOrder(bar_dict[target_future].last))
                    sell_open(target_future, abs(int(lot * context.sma_scores[key] / 3)),
                              style=LimitOrder(bar_dict[target_future].last))
        i += 1
    except Exception as e:
        logger.warn(key)
        logger.warn(e)
    finally:
        i += 1


def change_dominant(context, bar_dict):
    s1 = context.last_symbol

    for i in range(0, len(s1)):
        if context.last_symbol[i] != context.rolling_future[i]:
            print('换月合约：{}'.format(context.last_symbol[i]))
            if len(context.portfolio.positions) != 0:
                if context.portfolio.positions[context.rolling_future[i]].sell_quantity != 0:
                    long_position = context.portfolio.future_account.positions[context.rolling_future[i]].buy_quantity
                    short_position = context.portfolio.future_account.positions[context.rolling_future[i]].sell_quantity
                    # 平空仓
                    buy_close(context.rolling_future[i], short_position,
                              style=LimitOrder(bar_dict[context.rolling_future[i]].last))
                    # 换仓
                    sell_open(context.last_symbol[i], short_position,
                              style=LimitOrder(bar_dict[context.last_symbol[i]].last))
                elif context.portfolio.positions[context.rolling_future[i]].buy_quantity != 0:
                    long_position = context.portfolio.future_account.positions[context.rolling_future[i]].buy_quantity
                    short_position = context.portfolio.future_account.positions[context.rolling_future[i]].sell_quantity
                    # 平多仓
                    sell_close(context.rolling_future[i], long_position,
                               style=LimitOrder(bar_dict[context.rolling_future[i]].last))
                    # 换仓
                    buy_open(context.last_symbol[i], long_position,
                             style=LimitOrder(bar_dict[context.last_symbol[i]].last))

    unsubscribe(context.rolling_future)
    context.rolling_future = context.last_symbol
    subscribe(context.rolling_future)


