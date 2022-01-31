from functools import lru_cache

from binance.client import Client
from decouple import AutoConfig


class Binance:
    def __init__(self):
        self._config = AutoConfig()
        self.client = None

    def _connect(self):
        if not self.client:
            try:
                api_key = self._config('api_key')
                api_secret = self._config('api_secret')
                self.client = Client(api_key, api_secret)
            except:
                print(".env file not found")
                exit(-1)
        return

    def get_klines(self, p_interval, p_limit, p_symbol):
        self._connect()
        return self.client.get_klines(symbol=p_symbol, interval=p_interval, limit=p_limit)

    @lru_cache(maxsize=128)
    def get_symbol_info(self, symbol):
        self._connect()
        return self.client.get_symbol_info(symbol)

    def get_quote_asset_balance(self, symbol_info):
        self._connect()
        return float(self.client.get_asset_balance(asset=symbol_info['quoteAsset'])['free'])

    def get_base_asset_balance(self, symbol_info):
        self._connect()
        return float(self.client.get_asset_balance(asset=symbol_info['baseAsset'])['free'])

    def get_order_limit_buy(self, p, q, symbol):
        self._connect()
        return self.client.order_limit_buy(symbol=symbol, quantity=q, price=p)

    def get_order_limit_sell(self, p, q, symbol):
        self._connect()
        return self.client.order_limit_sell(symbol=symbol, quantity=q, price=p)

    def get_order(self, p_order_id, p_symbol):
        self._connect()
        return self.client.get_order(symbol=p_symbol, orderId=p_order_id)
