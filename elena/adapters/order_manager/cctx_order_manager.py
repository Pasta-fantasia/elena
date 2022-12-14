from typing import Dict, Optional

from elena.domain.model.order import Order
from elena.domain.model.order import OrderSide, OrderType
from elena.domain.model.trading_pair import TradingPair
from elena.domain.ports.logger import Logger
from elena.domain.ports.order_manager import OrderManager


class CctxOrderManager(OrderManager):

    def __init__(self, config: Dict, logger: Logger):
        self._config = config
        self._logger = logger

    def place(
            self,
            pair: TradingPair,
            type: OrderType,
            side: OrderSide,
            amount: float,
            price: Optional[float] = None,
            params: Dict = {}
    ) -> Order:
        """
        Places an order to an Exchange
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
            id: str,
            pair: TradingPair,
            params: Dict = {}
    ) -> Order:
        """
        Cancels an order on a Exchange
        :param id: the order id to cancel
        :param pair: the order pair (required by some exchanges)
        :param params: Extra parameters specific to the exchange API endpoint
        """
        pass

    def fetch(
            self,
            id: str,
            pair: TradingPair,
            params: Dict = {}
    ) -> Order:
        """
        Retrieves an order from Exchange
        :param id: the order id to retrieve
        :param pair: the order pair (required by some exchanges)
        :param params: Extra parameters specific to the exchange API endpoint
        """
        pass
