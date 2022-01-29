from enum import Enum
from functools import lru_cache

import pandas as pd
from binance.client import Client
from decouple import config

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

        candles = self._get_klines(p_interval, p_limit, p_symbol)
        candles_df = pd.DataFrame(candles)
        candles_df.columns = ['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume',
                              'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume',
                              'Ignore']
        candles_df["High"] = pd.to_numeric(candles_df["High"], downcast="float")
        candles_df["Low"] = pd.to_numeric(candles_df["Low"], downcast="float")
        candles_df["Close"] = pd.to_numeric(candles_df["Close"], downcast="float")

        return candles_df

    def _get_klines(self, p_interval, p_limit, p_symbol):
        return self.client.get_klines(symbol=p_symbol, interval=p_interval, limit=p_limit)

    @lru_cache(maxsize=128)
    def _get_symbol_info(self, symbol):
        return self.client.get_symbol_info(symbol)

    def _round_buy_sell_for_filters(self, p_symbol='ETHBUSD', buy_coin=True, amount=0.0):
        def truncate(n, decimals=0):
            multiplier = 10 ** decimals
            return int(n * multiplier) / multiplier

        symbol_info = self._get_symbol_info(p_symbol)

        for _filter in symbol_info['filters']:
            if _filter['filterType'] == 'PRICE_FILTER':
                tick_size = _filter['tickSize']
            if _filter['filterType'] == 'LOT_SIZE':
                step_size = _filter['stepSize']

        if buy_coin:
            fraction = float(step_size)
        else:
            fraction = float(tick_size)

        decimal_places = int(f'{fraction:e}'.split('e')[-1]) * -1
        amount = truncate(amount, decimal_places)

        amt_str = "{:0.0{}f}".format(amount, decimal_places)
        return amt_str

    def create_buy_order(self, max_order, symbol, buy_price):
        self._connect_client()
        quantity = max_order / buy_price

        symbol_info = self._get_symbol_info(symbol=symbol)
        free_balance = self._get_quote_asset_balance(symbol_info)
        if max_order > free_balance:
            # rounds may decrease balance in the quoteAsset
            quantity = free_balance / buy_price
            llog('buy using balance')

        q = self._round_buy_sell_for_filters(symbol, buy_coin=True, amount=quantity)
        p = self._round_buy_sell_for_filters(symbol, buy_coin=False, amount=buy_price)

        buy_order_id = 0
        try:
            order = self._get_order_limit_buy(p, q, symbol)
            buy_order_id = order['orderId']
        except:
            llog("error buying", q, p, 'max_order:' + max_order, 'buy_price:' + buy_price, 'symbol:' + symbol),

        return buy_order_id

    def _get_quote_asset_balance(self, symbol_info):
        self._connect_client()
        return float(self.client.get_asset_balance(asset=symbol_info['quoteAsset'])['free'])

    def _get_order_limit_buy(self, p, q, symbol):
        return self.client.order_limit_buy( symbol=symbol, quantity=q, price=p)

    def create_sell_order(self, symbol, buy_order_id, sell):
        self._connect_client()
        o = self._get_order(buy_order_id, symbol)
        sell_client_order_id = ''

        if o['status'] == OrderStatus.FILLED.value:
            sell_quantity = float(o['executedQty'])
            symbol_info = self._get_symbol_info(symbol=symbol)
            free_balance = self._get_base_asset_balance(symbol_info)

            if sell_quantity > free_balance:
                # if the order was processed as "taker" we don't have the information about the fee
                sell_quantity = free_balance
                llog('sell using balance')

            q = self._round_buy_sell_for_filters(symbol, buy_coin=True, amount=sell_quantity)
            p = self._round_buy_sell_for_filters(symbol, buy_coin=False, amount=sell)
            order_sell = self._get_order_limit_sell(p, q, symbol)
            sell_client_order_id = order_sell['orderId']
        return sell_client_order_id

    def _get_base_asset_balance(self, symbol_info):
        return float(self.client.get_asset_balance(asset=symbol_info['baseAsset'])['free'])

    def _get_order_limit_sell(self, p, q, symbol):
        return self.client.order_limit_sell(symbol=symbol, quantity=q, price=p)

    def check_order_status(self, p_symbol, p_order_id):
        self._connect_client()
        o = self._get_order(p_order_id, p_symbol)
        order_update_time = int(o['updateTime'])
        return o['status'], order_update_time

    def _get_order(self, p_order_id, p_symbol):
        return self.client.get_order(symbol=p_symbol, orderId=p_order_id)
