import sys
import os
import time
import json
import logging

import pandas as pd
import numpy as np

from elena.logging import llog
from elena.exchange import Exchange
from elena.elena_bot import read_state
from elena.elena_bot import save_state
from elena.utils import get_time

# Algorithm


def buy_sell(candles_df_buy_sell, algo, margin, tendence_tolerance):
    avg_price = candles_df_buy_sell["Close"].mean()
    # candles_df_buy_sell['avg_price']=avg_price

    regression = np.polyfit(candles_df_buy_sell.index, candles_df_buy_sell["Close"], 1)
    tendence = regression[0]

    if tendence > tendence_tolerance:
        if algo == 0:
            margin_local = margin * (2 / 3)
            buy = avg_price * (1 - ((margin_local / 2) / 100))
            buy = buy.astype(float)
            sell = avg_price * (1 + ((margin_local) / 100))
        if algo == 1:
            buy = candles_df_buy_sell['Close'][candles_df_buy_sell.index[-1]]
            buy = buy.astype(float)
            sell = buy * (1 + ((margin) / 100))
        if algo == 2:
            buy = candles_df_buy_sell['High'][candles_df_buy_sell.index[-1]]
            buy = buy.astype(float)
            sell = buy * (1 + ((margin) / 100))
    else:
        sell = 0
        buy = 0

    return buy, sell


# Elena

def estimate_buy_sel(exchange, p_elena):
    candles_df = exchange.get_candles(p_symbol=p_elena['symbol'], p_limit=p_elena['data_samples'])
    return buy_sell(candles_df, p_elena['algo'], p_elena['margin'], p_elena['tendence_tolerance'])


def sleep_until(sell_execution_time, minutes):
    return sell_execution_time + minutes * 60 * 1000  # 45' after the sale


# Elena - State machine
def iterate(p_robot_filename, exchange, p_elena):
    if p_elena['sleep_until'] < get_time():

        if not p_elena['buy_order_id'] and p_elena['active']:
            buy, sell = estimate_buy_sel(exchange, p_elena)
            if buy > 0:
                llog("create a new buy order")
                new_buy_order_id = exchange.create_buy_order(p_elena, buy)
                p_elena['sleep_until'] = 0
                p_elena['buy_order_id'] = new_buy_order_id
                p_elena['sell_order_id'] = ''
                p_elena['buy'] = buy
                p_elena['sell'] = sell
                save_state(p_robot_filename, p_elena)
            else:
                p_elena['sleep_until'] = sleep_until(get_time(), 5)
                save_state(p_robot_filename, p_elena)
                llog("don't buy")
            return

        if p_elena['buy_order_id'] and not p_elena['sell_order_id']:
            new_sell_order_id = exchange.create_sell_order(p_elena)
            if new_sell_order_id:
                llog("create a new sell order")
                p_elena['sell_order_id'] = new_sell_order_id
                save_state(p_robot_filename, p_elena)
            else:
                status = exchange.check_buy_order_execution_status(p_elena)
                if not status == 'CANCELED':
                    p_elena['sleep_until'] = sleep_until(get_time(), 5)
                    save_state(p_robot_filename, p_elena)
                    llog("waiting purchase")
                else:
                    llog("cancellation")
                    save_state('history/' + str(get_time()) + '_' + str(p_elena['buy_order_id']) + '.json', p_elena)
                    p_elena['sleep_until'] = sleep_until(get_time(), 5)
                    p_elena['buy_order_id'] = ''
                    p_elena['sell_order_id'] = ''
                    p_elena['buy'] = 0
                    p_elena['sell'] = 0
                    save_state(p_robot_filename, p_elena)
            return

        if p_elena['buy_order_id'] and p_elena['sell_order_id']:
            sell_execution_time = exchange.check_sell_order_execution_time(p_elena)
            if sell_execution_time > 0:
                llog("save history")
                save_state('history/' + str(get_time()) + '_' + str(p_elena['buy_order_id']) + '.json', p_elena)
                llog("set sleep")
                p_elena['sleep_until'] = sleep_until(sell_execution_time, p_elena['data_samples'] * 1.5)
                p_elena['buy_order_id'] = ''
                p_elena['sell_order_id'] = ''
                p_elena['buy'] = 0
                p_elena['sell'] = 0
                save_state(p_robot_filename, p_elena)
            else:
                p_elena['sleep_until'] = sleep_until(get_time(), 15)
                save_state(p_robot_filename, p_elena)
                llog("waiting sell")
            return
    else:
        llog("sleeping")


binance = Exchange()

if len(sys.argv) > 1:
    robots = [sys.argv[1]]
else:
    robots = []
    dire = '.'
    for filename in os.listdir(dire):
        if filename.endswith('.json'):
            f = os.path.join(dire, filename)
            robots.append(f)

for robot_filename in robots:
    logging.basicConfig(filename='elena.log', level=logging.INFO, format='%(asctime)s %(message)s')
    llog(robot_filename)
    elena = read_state(robot_filename)
    iterate(robot_filename, binance, elena)
