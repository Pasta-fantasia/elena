import logging
import os
import sys

import numpy as np

from elena.elena_bot import Elena
from elena.exchange import Exchange
from elena.exchange import OrderStatus
from elena.logging import llog
from elena.utils import get_time


# Algorithm


def buy_sell(candles_df_buy_sell, algo, margin, tendence_tolerance):
    sell = 0
    buy = 0
    avg_price = candles_df_buy_sell["Close"].mean()
    # candles_df_buy_sell['avg_price']=avg_price

    regression = np.polyfit(candles_df_buy_sell.index, candles_df_buy_sell["Close"], 1)
    tendence = regression[0]

    if tendence > tendence_tolerance:
        if algo == 0:
            margin_local = margin * (2 / 3)
            buy = avg_price * (1 - ((margin_local / 2) / 100))
            buy = buy.astype(float)
            sell = avg_price * (1 + (margin_local / 100))
        if algo == 1:
            buy = candles_df_buy_sell['Close'][candles_df_buy_sell.index[-1]]
            buy = buy.astype(float)
            sell = buy * (1 + (margin / 100))
        if algo == 2:
            buy = candles_df_buy_sell['High'][candles_df_buy_sell.index[-1]]
            buy = buy.astype(float)
            sell = buy * (1 + (margin / 100))
        if algo == 4:
            regression_low = np.polyfit(candles_df_buy_sell.index, candles_df_buy_sell["Low"], 1)
            next_low = regression_low[0] * (candles_df_buy_sell.index[-1] + 1) + regression_low[1]

            regression_close = np.polyfit(candles_df_buy_sell.index, candles_df_buy_sell["Close"], 1)
            next_close = regression_close[0] * (candles_df_buy_sell.index[-1] + 1) + regression_close[1]

            if next_close / next_low > 1.0005:  # ensure sell is higher than buy at least by 5 per thousand to pay fees
                buy = next_low
                sell = next_close
        if algo == 5:
            regression_low = np.polyfit(candles_df_buy_sell.index, candles_df_buy_sell["Low"], 1)
            next_low = regression_low[0] * (candles_df_buy_sell.index[-1] + 1) + regression_low[1]

            regression_close = np.polyfit(candles_df_buy_sell.index, candles_df_buy_sell["High"], 1)
            next_high = regression_close[0] * (candles_df_buy_sell.index[-1] + 1) + regression_close[1]

            if next_high / next_low > 1.0005:  # ensure sell is higher than buy at least by 5 per thousand to pay fees
                buy = next_low
                sell = next_high
    if algo == 3:
        regression_low = np.polyfit(candles_df_buy_sell.index, candles_df_buy_sell["Low"], 1)
        next_low = regression_low[0] * (candles_df_buy_sell.index[-1] + 1) + regression_low[1]

        regression_close = np.polyfit(candles_df_buy_sell.index, candles_df_buy_sell["Close"], 1)
        next_close = regression_close[0] * (candles_df_buy_sell.index[-1] + 1) + regression_close[1]

        if next_close / next_low > 1.0005:  # ensure sell is higher than buy at least by 5 per thousand to pay fees
            buy = next_low
            sell = next_close

    return buy, sell


# Elena - State machine
def iterate(p_robot_filename, exchange, elena):
    state = elena.read_state(robot_filename)
    if state['sleep_until'] < get_time():

        if not state['buy_order_id'] and state['active']:
            buy, sell = elena.estimate_buy_sel(exchange, state, buy_sell)
            if buy > 0:
                llog("create a new buy order")
                new_buy_order_id = exchange.create_buy_order(state['max_order'], state['symbol'], buy)
                state['sleep_until'] = 0
                state['buy_order_id'] = new_buy_order_id
                state['sell_order_id'] = ''
                state['buy'] = buy
                state['sell'] = sell
                elena.save_state(p_robot_filename, state)
            else:
                state['sleep_until'] = elena.sleep_until(get_time(), 5)
                elena.save_state(p_robot_filename, state)
                llog("don't buy")
            return

        if state['buy_order_id'] and not state['sell_order_id']:
            new_sell_order_id = exchange.create_sell_order(state['symbol'], state['buy_order_id'], state['sell'])
            if new_sell_order_id:
                llog("create a new sell order")
                state['sell_order_id'] = new_sell_order_id
                elena.save_state(p_robot_filename, state)
            else:
                status, order_update_time = exchange.check_order_status(state['symbol'], state['buy_order_id'])
                if not status == OrderStatus.CANCELED.value:
                    state['sleep_until'] = elena.sleep_until(get_time(), 5)
                    elena.save_state(p_robot_filename, state)
                    llog("waiting purchase")
                else:
                    llog("buy cancellation")
                    elena.save_state('history/' + str(get_time()) + '_' + str(state['buy_order_id']) + '.json', state)
                    state['sleep_until'] = 0
                    state['buy_order_id'] = ''
                    state['sell_order_id'] = ''
                    state['buy'] = 0
                    state['sell'] = 0
                    elena.save_state(p_robot_filename, state)
            return

        if state['buy_order_id'] and state['sell_order_id']:
            status, order_update_time = exchange.check_order_status(state['symbol'], state['sell_order_id'])
            if status == OrderStatus.FILLED.value:
                llog("save history")
                elena.save_state('history/' + str(get_time()) + '_' + str(state['buy_order_id']) + '.json', state)
                llog("set sleep")
                state['sleep_until'] = elena.sleep_until(order_update_time, state['data_samples'] * 1.5)
                state['buy_order_id'] = ''
                state['sell_order_id'] = ''
                state['buy'] = 0
                state['sell'] = 0
                elena.save_state(p_robot_filename, state)
            elif status == OrderStatus.CANCELED.value:
                llog("sell cancellation, save history")
                elena.save_state('history/' + str(get_time()) + '_' + str(state['buy_order_id']) + '.json', state)
                state['active'] = 0
                state['buy_order_id'] = ''
                state['sell_order_id'] = ''
                state['buy'] = 0
                state['sell'] = 0
                elena.save_state(p_robot_filename, state)
            else:
                state['sleep_until'] = elena.sleep_until(get_time(), 15)
                elena.save_state(p_robot_filename, state)
                llog("waiting sell")
            return
    else:
        llog("sleeping")


binance = Exchange()
logging.basicConfig(filename='elena.log', level=logging.INFO, format='%(asctime)s %(message)s')

if len(sys.argv) > 1:
    robots = [sys.argv[1]]
else:
    robots = []
    dire = '.'
    for filename in os.listdir(dire):
        if filename.endswith('.json'):
            f = os.path.join(dire, filename)
            robots.append(f)

llog('time', get_time())
for robot_filename in robots:
    llog(robot_filename)
    _elena = Elena()
    iterate(robot_filename, binance, _elena)
