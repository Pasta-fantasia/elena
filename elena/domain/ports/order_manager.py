from typing import Protocol, Dict, Optional

from elena.domain.model.bot_config import BotConfig
from elena.domain.model.exchange import Exchange
from elena.domain.model.order import Order, OrderSide, OrderType


class OrderManager(Protocol):

    def place(
            self,
            exchange: Exchange,
            bot_config: BotConfig,
            type: OrderType,
            side: OrderSide,
            amount: float,
            price: Optional[float] = None,
            params: Dict = {}
    ) -> Order:
        """
        Places an order to an Exchange
        :param exchange: exchange where to read market data
        :param bot_config: the current bot configuration
        :param pair: the order pair
        :param type: the type of your order
        :param side: the direction of your order
        :param amount: how much of currency you want to trade
        :param price: the price at which the order is to be fulfilled (ignored in market orders)
        :param params: Extra parameters specific to the exchange API endpoint
        :return: the placed Order, error if any
        """
        pass

    def cancel(
            self,
            id: str,
            exchange: Exchange,
            bot_config: BotConfig,
            params: Dict = {}
    ):
        """
        Cancels an order on a Exchange
        :param exchange: exchange where to read market data
        :param bot_config: the current bot configuration
        :param id: the order id to cancel
        :param params: Extra parameters specific to the exchange API endpoint
        :return: error if any
        """
        pass

    def fetch(
            self,
            id: str,
            exchange: Exchange,
            bot_config: BotConfig,
            params: Dict = {}
    ) -> Order:
        """
        Retrieves an order from Exchange
        :param exchange: exchange where to read market data
        :param bot_config: the current bot configuration
        :param id: the order id to retrieve
        :param params: Extra parameters specific to the exchange API endpoint
        :return: the list of orders, error if any
        """
        pass
