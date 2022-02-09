from enum import Enum

import pandas as pd
from binance.client import Client

from elena import utils
from elena.binance import Binance
from elena.logging import llog


# Exchange

# Duplicated from Binance. Done from decouple from Binance module
# TODO: don't use Enum this is not Pascal :)
class OrderStatus(Enum):
    NEW = 'NEW'
    PARTIALLY_FILLED = 'PARTIALLY_FILLED'
    FILLED = 'FILLED'
    CANCELED = 'CANCELED'
    PENDING_CANCEL = 'PENDING_CANCEL'
    REJECTED = 'REJECTED'
    EXPIRED = 'EXPIRED'


class Exchange:
    def __init__(self, api: Binance):
        self._api = api
        self._rec = utils.TestDataRecorder('Exchange', '../../test_data')

    def start_recorder(self):
        self._rec.start()

    def stop_recorder(self):
        self._rec.stop()

    def get_candles(self, p_symbol='ETHBUSD', p_interval=Client.KLINE_INTERVAL_1MINUTE, p_limit=1000):
        self._rec.func_in('get_candles', p_symbol=p_symbol, p_interval=p_interval, p_limit=p_limit)

        self._rec.call_in('get_candles', '_api.get_klines', p_interval=p_interval, p_limit=p_limit, p_symbol=p_symbol)
        candles = self._api.get_klines(p_interval, p_limit, p_symbol)
        self._rec.call_out('get_candles', '_api.get_klines', candles=candles)

        candles_df = pd.DataFrame(candles)
        candles_df.columns = ['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume',
                              'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume',
                              'Ignore']
        candles_df["High"] = pd.to_numeric(candles_df["High"], downcast="float")
        candles_df["Low"] = pd.to_numeric(candles_df["Low"], downcast="float")
        candles_df["Close"] = pd.to_numeric(candles_df["Close"], downcast="float")

        self._rec.func_out('get_candles', candles_df=candles_df.to_json())
        return candles_df

    def _round_buy_sell_for_filters(self, p_symbol='ETHBUSD', buy_coin=True, amount=0.0):
        def truncate(n, decimals=0):
            multiplier = 10 ** decimals
            return int(n * multiplier) / multiplier

        symbol_info = self._api.get_symbol_info(p_symbol)
        step_size = -1
        tick_size = -1
        for _filter in symbol_info['filters']:
            if _filter['filterType'] == 'PRICE_FILTER':
                tick_size = _filter['tickSize']
            if _filter['filterType'] == 'LOT_SIZE':
                step_size = _filter['stepSize']

        if step_size == -1 or tick_size == -1:
            raise RuntimeError('error: undefined PRICE_FILTER and LOT_SIZE')

        if buy_coin:
            fraction = float(step_size)
        else:
            fraction = float(tick_size)

        decimal_places = int(f'{fraction:e}'.split('e')[-1]) * -1
        amount = truncate(amount, decimal_places)

        amt_str = "{:0.0{}f}".format(amount, decimal_places)
        return amt_str

    def get_order(self, p_order_id, p_symbol):
        return self._api.get_order(p_order_id, p_symbol)

    def create_buy_order(self, max_order, symbol, buy_price):
        quantity = max_order / buy_price

        symbol_info = self._api.get_symbol_info(symbol=symbol)
        free_balance = self._api.get_asset_balance(symbol_info['quoteAsset'])
        if max_order > free_balance:
            # rounds may decrease balance in the quoteAsset
            quantity = free_balance / buy_price
            llog('buy using balance')

        q = self._round_buy_sell_for_filters(symbol, buy_coin=True, amount=quantity)
        p = self._round_buy_sell_for_filters(symbol, buy_coin=False, amount=buy_price)

        buy_order_id = 0
        try:
            order = self._api.get_order_limit_buy(p, q, symbol)
            buy_order_id = order['orderId']
        except:
            llog("error buying", q, p, 'max_order:' + max_order, 'buy_price:' + buy_price, 'symbol:' + symbol),

        return buy_order_id

    def create_sell_order(self, symbol, buy_order_id, sell):
        o = self.get_order(buy_order_id, symbol)
        sell_client_order_id = ''

        if o['status'] == OrderStatus.FILLED.value:
            sell_quantity = float(o['executedQty'])
            symbol_info = self._api.get_symbol_info(symbol=symbol)
            free_balance = self._api.get_asset_balance(symbol_info['baseAsset'])

            if sell_quantity > free_balance:
                # if the order was processed as "taker" we don't have the information about the fee
                sell_quantity = free_balance
                llog('sell using balance')

            q = self._round_buy_sell_for_filters(symbol, buy_coin=True, amount=sell_quantity)
            p = self._round_buy_sell_for_filters(symbol, buy_coin=False, amount=sell)
            order_sell = self._api.get_order_limit_sell(p, q, symbol)
            sell_client_order_id = order_sell['orderId']
        return sell_client_order_id

    def check_order_status(self, p_symbol, p_order_id):
        o = self.get_order(p_order_id, p_symbol)
        order_update_time = int(o['updateTime'])
        return o['status'], order_update_time
