import sys
import time
import json
import logging
from logging.config import dictConfig

from binance.client import Client
from decouple import config

import pandas as pd
import numpy as np


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


# Logs
def llog(m):
    logging.info(m)


# Exchange

class Exchange:
    def __init__(self):
        self.client = None
        self.symbol_info = None

    def connect_client(self):
        if not self.client:
            api_key = config('api_key')
            api_secret = config('api_secret')
            self.client = Client(api_key, api_secret)
        return

    def get_candles(self, p_symbol='ETHBUSD', p_interval=Client.KLINE_INTERVAL_1MINUTE, p_limit=1000):
        self.connect_client()

        candles = self.client.get_klines(symbol=p_symbol, interval=p_interval, limit=p_limit)

        candles_df = pd.DataFrame(candles)
        candles_df.columns = ['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume',
                              'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume',
                              'Ignore']
        candles_df["High"] = pd.to_numeric(candles_df["High"], downcast="float")
        candles_df["Low"] = pd.to_numeric(candles_df["Low"], downcast="float")
        candles_df["Close"] = pd.to_numeric(candles_df["Close"], downcast="float")

        return candles_df

    def round_buy_sell_for_filters(self, p_symbol='ETHBUSD', buy_coin=True, amount=0):
        def truncate(n, decimals=0):
            multiplier = 10 ** decimals
            return int(n * multiplier) / multiplier

        self.connect_client()
        symbol_info = self.client.get_symbol_info(p_symbol)

        for filter in symbol_info['filters']:
            if filter['filterType'] == 'PRICE_FILTER':
                tickSize = filter['tickSize']
            if filter['filterType'] == 'LOT_SIZE':
                stepSize = filter['stepSize']

        if buy_coin:
            fraction = float(stepSize)
        else:
            fraction = float(tickSize)

        decimal_places = int(f'{fraction:e}'.split('e')[-1]) * -1
        amount = truncate(amount, decimal_places)

        amt_str = "{:0.0{}f}".format(amount, decimal_places)
        return amt_str

    def create_buy_order_test(self, p_elena, buy):
        return "hola"

    def create_buy_order(self, p_elena, buy):
        self.connect_client()

        quantity = p_elena['max_order'] / buy

        q = self.round_buy_sell_for_filters(p_elena['symbol'], buy_coin=True, amount=quantity)
        p = self.round_buy_sell_for_filters(p_elena['symbol'], buy_coin=False, amount=buy)
        order = self.client.order_limit_buy(
            symbol=p_elena['symbol'],
            quantity=q,
            price=p)
        return order['orderId']

    def create_sell_order(self, p_elena):
        self.connect_client()
        o = self.client.get_order(symbol=p_elena['symbol'], orderId=p_elena['buy_order_id'])
        sell_client_order_id = ''

        if o['status'] == 'FILLED':
            sell_quantity = float(o['executedQty'])
            symbol_info = self.client.get_symbol_info(symbol=p_elena['symbol'])
            free_balance = float(self.client.get_asset_balance(asset=symbol_info['baseAsset'])['free'])

            if sell_quantity > free_balance:
                # if the order was processed as "taker" we don't have the information about the fee
                sell_quantity = free_balance
                llog('sell using balance')

            q = self.round_buy_sell_for_filters(p_elena['symbol'], buy_coin=True, amount=sell_quantity)
            p = self.round_buy_sell_for_filters(p_elena['symbol'], buy_coin=False, amount=p_elena['sell'])
            order_sell = self.client.order_limit_sell(
                symbol=p_elena['symbol'],
                quantity=q,
                price=p)
            sell_client_order_id = order_sell['orderId']
        return sell_client_order_id

    def check_buy_order_execution_status(self, p_elena):
        self.connect_client()
        o = self.client.get_order(symbol=p_elena['symbol'], orderId=p_elena['buy_order_id'])
        return o['status']

    def check_sell_order_execution_time(self, p_elena):
        # find the updateTime of the full filled sell ('status': 'FILLED')
        self.connect_client()
        o = self.client.get_order(symbol=p_elena['symbol'], orderId=p_elena['sell_order_id'])
        sell_updateTime = 0
        if o['status']=='FILLED':
            sell_updateTime=int(o['updateTime'])
        return sell_updateTime


# General functions
def get_time():
    return int(time.time() * 1000)


def read_state(p_robot_filename):
    fp = open(p_robot_filename, 'r')
    elena = json.load(fp)
    fp.close()
    return elena


def save_state(p_robot_filename, p_elena):
    fp = open(p_robot_filename, 'w')
    json.dump(p_elena, fp)
    fp.close()


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


robot_filename = sys.argv[1]
logging.basicConfig(filename=robot_filename+'.log',level=logging.INFO, format='%(asctime)s %(message)s')
binance = Exchange()
elena = read_state(robot_filename)
iterate(robot_filename, binance, elena)
