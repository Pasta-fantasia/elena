from binance.client import Client
from decouple import config

import pandas as pd
import numpy as np


# Exchange

class Exchange:
    def __init__(self):
        self.client = None
        self.symbol_info = None

    def connect_client(self):
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