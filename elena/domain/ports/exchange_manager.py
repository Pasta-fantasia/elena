from typing import Protocol, Optional, Dict

import pandas as pd

from elena.domain.model.balance import Balance
from elena.domain.model.bot_config import BotConfig
from elena.domain.model.exchange import Exchange
from elena.domain.model.order import Order, OrderSide, OrderType
from elena.domain.model.order_book import OrderBook
from elena.domain.model.time_frame import TimeFrame
from elena.domain.model.trading_pair import TradingPair


class ExchangeManager(Protocol):

    def read_candles(
            self,
            exchange: Exchange,
            pair: TradingPair,
            time_frame: TimeFrame = TimeFrame.min_1
    ) -> pd.DataFrame:
        """
        Reads market candles from exchange
        :param exchange: exchange where to read market data
        :param pair: trading pair to read
        :param time_frame: time frame to read
        :return: the market candles
        """
        ...

    def amount_to_precision(
            self,
            exchange: Exchange,
            pair: TradingPair,
            amount: float
    ) -> float:
        ...

    def price_to_precision(
            self,
            exchange: Exchange,
            pair: TradingPair,
            price: float
    ) -> float:
        ...


    def read_order_book(
            self,
            exchange: Exchange,
            pair: TradingPair
    ) -> OrderBook:
        """
        Reads exchange order book
        :param exchange: exchange where to read exchange data
        :param pair: trading pair to read
        :return: the current order book
        """
        ...



    def get_balance(
            self,
            exchange: Exchange
    ) -> Balance:
        """
        Gets the amount of funds available for trading or funds locked in orders
        :param exchange: exchange where to read market data
        :return: The balance
        """
        ...

    def place_order(
            self,
            exchange: Exchange,
            bot_config: BotConfig,
            order_type: OrderType,
            side: OrderSide,
            amount: float,
            price: Optional[float] = None,
            params: Optional[Dict] = {}
    ) -> Order:
        """
        Places an order to an Exchange
        :param exchange: exchange where to read market data
        :param bot_config: the current bot configuration
        :param order_type: the type of your order
        :param side: the direction of your order
        :param amount: how much of currency you want to trade
        :param price: the price at which the order is to be fulfilled (ignored in market orders)
        :param dict [params]: extra parameters specific to the exchange api endpoint, check https://docs.ccxt.com/#/README?id=orders
        :return: the placed Order, error if any
        """
        ...

    def cancel_order(
            self,
            exchange: Exchange,
            bot_config: BotConfig,
            order_id: str
    ):
        """
        Cancels an order on a Exchange
        :param exchange: exchange where to read market data
        :param bot_config: the current bot configuration
        :param order_id: the order id to cancel_order
        :return: error if any
        """
        ...

    def fetch_order(
            self,
            exchange: Exchange,
            bot_config: BotConfig,
            order_id: str
    ) -> Order:
        """
        Retrieves an order from Exchange
        :param exchange: exchange where to read market data
        :param bot_config: the current bot configuration
        :param order_id: the order id to retrieve
        :return: the list of orders, error if any
        """
        ...
