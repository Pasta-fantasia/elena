from abc import ABC, abstractmethod


class Exchange(ABC):

    @abstractmethod
    def get_minimum_profit(self) -> float:
        pass

    @abstractmethod
    def get_klines(self, p_interval, p_limit, p_symbol):
        pass

    @abstractmethod
    def get_cached_symbol_info(self, symbol):
        pass

    @abstractmethod
    def get_cached_avg_price(self, symbol):
        pass

    @abstractmethod
    def get_asset_balance(self, asset):
        pass

    @abstractmethod
    def order_limit_buy(self, p, q, symbol):
        pass

    @abstractmethod
    def order_limit_sell(self, p, q, symbol):
        pass

    @abstractmethod
    def get_order(self, p_order_id, p_symbol):
        pass

    @abstractmethod
    def get_cached_order_book_first_bids_asks(self, p_symbol):
        pass

    @abstractmethod
    def convert_to_usd(self, symbol, quantity):
        pass
