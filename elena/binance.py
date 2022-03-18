from functools import lru_cache

from binance.client import Client
from decouple import AutoConfig
from elena.logging import llog


class Binance:
    def __init__(self):
        self._config = AutoConfig()
        self.client = None
        self.minimum_profit = 1.005

    def _connect(self):
        if not self.client:
            try:
                api_key = self._config('api_key')
                api_secret = self._config('api_secret')
                self.client = Client(api_key, api_secret)
            except Exception as e:
                llog(".env file not found or connection error")
                llog(e)
                exit(-1)
        return

    def get_klines(self, p_interval, p_limit, p_symbol):
        self._connect()
        return self.client.get_klines(symbol=p_symbol, interval=p_interval, limit=p_limit)

    @lru_cache()
    def get_cached_symbol_info(self, symbol):
        self._connect()
        return self.client.get_symbol_info(symbol)

    @lru_cache()
    def get_cached_avg_price(self, symbol):
        self._connect()
        avg_price = self.client.get_avg_price(symbol=symbol)
        asset_fact = float(avg_price['price'])
        return asset_fact

    def get_asset_balance(self, asset):
        self._connect()
        return float(self.client.get_asset_balance(asset=asset)['free'])

    def order_limit_buy(self, p, q, symbol):
        self._connect()
        return self.client.order_limit_buy(symbol=symbol, quantity=q, price=p)

    def cancel_order(self, symbol, order_id):
        self._connect()
        return self.client.cancel_order(symbol=symbol, orderId=order_id)

    def order_limit_sell(self, p, q, symbol):
        self._connect()
        return self.client.order_limit_sell(symbol=symbol, quantity=q, price=p)

    def get_order(self, p_order_id, p_symbol):
        self._connect()
        return self.client.get_order(symbol=p_symbol, orderId=p_order_id)

    @lru_cache()
    def get_cached_order_book_first_bids_asks(self, p_symbol):
        self._connect()
        book = self.client.get_order_book(symbol=p_symbol)
        return float(book['bids'][0][0]), float(book['asks'][0][0])

    def convert_to_usd(self, symbol, quantity):
        if symbol.endswith('BUSD'):
            return quantity
        else:
            symbol_info = self.get_cached_symbol_info(symbol)
            asset_busd = symbol_info['quoteAsset'] + 'BUSD'
            # TODO: use try
            return quantity * self.get_cached_avg_price(asset_busd)
