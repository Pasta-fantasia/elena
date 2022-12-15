from typing import Dict, Optional

from elena.adapters.common import common_cctx
from elena.domain.model.exchange import Exchange
from elena.domain.model.order import Order
from elena.domain.model.order import OrderSide, OrderType
from elena.domain.model.trading_pair import TradingPair
from elena.domain.ports.logger import Logger
from elena.domain.ports.order_manager import OrderManager


class CctxOrderManager(OrderManager):

    def __init__(self, config: Dict, logger: Logger):
        self._config = config['CctxOrderManager']
        self._logger = logger

    def place(
            self,
            exchange: Exchange,
            pair: TradingPair,
            type: OrderType,
            side: OrderSide,
            amount: float,
            price: Optional[float] = None,
            params: Dict = {}
    ) -> Order:
        try:
            _conn = common_cctx.connect(exchange, self._logger)
            _order = _conn.create_order(
                symbol=str(pair),
                type=type.value,
                side=side.value,
                amount=amount,
                price=price,
                params=params
            )
        except Exception as err:
            raise err
        return self._map_order(_order)

    def _map_order(self, _order) -> Order:
        pass

    def cancel(
            self,
            exchange: Exchange,
            id: str,
            pair: TradingPair,
            params: Dict = {}
    ) -> Order:
        pass

    def fetch(
            self,
            exchange: Exchange,
            id: str,
            pair: TradingPair,
            params: Dict = {}
    ) -> Order:
        pass
