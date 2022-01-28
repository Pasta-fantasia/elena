from binance.client import Client
from decouple import config
from functools import lru_cache
from enum import Enum

import pandas as pd
import numpy as np

from elena.logging import llog


# Exchange

# Duplicated from Binance. Done from decouple from Binance module
class OrderStatus(Enum):
    NEW = 'NEW'
    PARTIALLY_FILLED = 'PARTIALLY_FILLED'
    FILLED = 'FILLED'
    CANCELED = 'CANCELED'
    PENDING_CANCEL = 'PENDING_CANCEL'
    REJECTED = 'REJECTED'
    EXPIRED = 'EXPIRED'


class Exchange:
    def __init__(self):
        self.client = None
        self.symbol_info = None

    def _connect_client(self):
        if not self.client:
            try:
                api_key = config('api_key')
                api_secret = config('api_secret')
                self.client = Client(api_key, api_secret)
            except:
                print(".env file not found")
                exit(-1)
        return

    def get_candles(self, p_symbol='ETHBUSD', p_interval=Client.KLINE_INTERVAL_1MINUTE, p_limit=1000):
        self._connect_client()

        # TODO: .client
        candles = self.client.get_klines(symbol=p_symbol, interval=p_interval, limit=p_limit)

        candles_df = pd.DataFrame(candles)
        candles_df.columns = ['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume',
                              'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume',
                              'Ignore']
        candles_df["High"] = pd.to_numeric(candles_df["High"], downcast="float")
        candles_df["Low"] = pd.to_numeric(candles_df["Low"], downcast="float")
        candles_df["Close"] = pd.to_numeric(candles_df["Close"], downcast="float")

        return candles_df

    @lru_cache(maxsize=128)
    def _get_symbol_info(self, symbol):
        self._connect_client()
        symbol_info = self.client.get_symbol_info(symbol)
        return symbol_info

    def _round_buy_sell_for_filters(self, p_symbol='ETHBUSD', buy_coin=True, amount=0):
        def truncate(n, decimals=0):
            multiplier = 10 ** decimals
            return int(n * multiplier) / multiplier

        self._connect_client()
        symbol_info = self._get_symbol_info(p_symbol)

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

    def create_buy_order(self, p_elena, buy_price):
        self._connect_client()

        quantity = p_elena['max_order'] / buy_price

        symbol_info = self._get_symbol_info(symbol=p_elena['symbol'])
        free_balance = float(self.client.get_asset_balance(asset=symbol_info['quoteAsset'])['free'])
        if p_elena['max_order'] > free_balance:
            # rounds may decrease balance in the quoteAsset
            quantity = free_balance / buy_price
            llog('buy using balance')

        q = self._round_buy_sell_for_filters(p_elena['symbol'], buy_coin=True, amount=quantity)
        p = self._round_buy_sell_for_filters(p_elena['symbol'], buy_coin=False, amount=buy_price)

        buy_order_id = 0
        try:
            order = self.client.order_limit_buy(
                symbol=p_elena['symbol'],
                quantity=q,
                price=p)
            buy_order_id = order['orderId']
        except:
            llog("error buying", q, p, p_elena)

        return buy_order_id

    def create_sell_order(self, p_elena):
        self._connect_client()
        # TODO: .client
        o = self.client.get_order(symbol=p_elena['symbol'], orderId=p_elena['buy_order_id'])
        sell_client_order_id = ''

        if o['status'] == OrderStatus.FILLED:
            sell_quantity = float(o['executedQty'])
            symbol_info = self._get_symbol_info(symbol=p_elena['symbol'])
            # TODO: .client
            free_balance = float(self.client.get_asset_balance(asset=symbol_info['baseAsset'])['free'])

            if sell_quantity > free_balance:
                # if the order was processed as "taker" we don't have the information about the fee
                sell_quantity = free_balance
                llog('sell using balance')

            q = self._round_buy_sell_for_filters(p_elena['symbol'], buy_coin=True, amount=sell_quantity)
            p = self._round_buy_sell_for_filters(p_elena['symbol'], buy_coin=False, amount=p_elena['sell'])
            # TODO: .client
            order_sell = self.client.order_limit_sell(
                symbol=p_elena['symbol'],
                quantity=q,
                price=p)
            sell_client_order_id = order_sell['orderId']
        return sell_client_order_id

    def check_order_status(self, p_elena):
        self._connect_client()
        # TODO: .client
        o = self.client.get_order(symbol=p_elena['symbol'], orderId=p_elena['buy_order_id'])
        order_update_time = int(o['updateTime'])
        return o['status'], order_update_time


