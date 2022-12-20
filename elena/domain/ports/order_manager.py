from typing import Protocol, Dict, Optional

from elena.domain.model.bot_config import BotConfig
from elena.domain.model.exchange import Exchange
from elena.domain.model.order import Order, OrderSide, OrderType
from elena.domain.model.trading_pair import TradingPair


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
        """
        pass

    def cancel(
            self,
            exchange: Exchange,
            id: str,
            pair: TradingPair,
            params: Dict = {}
    ) -> Order:
        """
        Cancels an order on a Exchange
        :param exchange: exchange where to read market data
        :param id: the order id to cancel
        :param pair: the order pair (required by some exchanges)
        :param params: Extra parameters specific to the exchange API endpoint
        """
        pass

    def fetch(
            self,
            id: str,
            exchange: Exchange,
            pair: TradingPair,
            params: Dict = {}
    ) -> Order:
        """
        Retrieves an order from Exchange
        :param exchange: exchange where to read market data
        :param id: the order id to retrieve
        :param pair: the order pair (required by some exchanges)
        :param params: Extra parameters specific to the exchange API endpoint
        """
        pass
