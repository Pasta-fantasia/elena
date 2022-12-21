from typing import Dict, Optional, List, Any

from elena.adapters.common import common_cctx
from elena.domain.model.bot_config import BotConfig
from elena.domain.model.currency import Currency
from elena.domain.model.exchange import Exchange
from elena.domain.model.order import Order, OrderStatusType, Trade, TakerOrMaker, Fee
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
            bot_config: BotConfig,
            type: OrderType,
            side: OrderSide,
            amount: float,
            price: Optional[float] = None,
            params: Dict = {}
    ) -> Order:
        try:
            _conn = common_cctx.connect(exchange, self._logger)
            _order = _conn.create_order(
                symbol=str(bot_config.pair),
                type=type.value,
                side=side.value,
                amount=amount,
                price=price,
                params=params
            )
            result = self._map_order(exchange, bot_config, bot_config.pair, _order)
            return result
        except Exception as err:
            raise err

    def _map_order(self, exchange: Exchange, bot_config: BotConfig, pair: TradingPair, order) -> Order:
        return Order(
            id=order['id'],
            exchange_id=exchange.id,
            bot_id=bot_config.id,
            strategy_id=bot_config.strategy_id,
            pair=pair,
            client_order_id=order['clientOrderId'],
            timestamp=order['timestamp'],
            last_trade_timestamp=order['lastTradeTimestamp'],
            type=OrderType(order['type']),
            side=OrderSide(order['side']),
            price=order['price'],
            amount=order['amount'],
            cost=order['cost'],
            average=order['average'],
            filled=order['filled'],
            remaining=order['remaining'],
            status=self._map_status(order['status']),
            trades=self._map_trades(order['trades']),
            fee=self._map_fee(order['fee']),
            info=order['info'],
        )

    @staticmethod
    def _map_status(status) -> Optional[OrderStatusType]:
        if status:
            return OrderStatusType(status)
        else:
            return None

    def _map_fee(self, fee) -> Optional[Fee]:
        if fee:
            return Fee(
                currency=Currency(self._nvl(fee, 'currency', 0.0)),
                cost=self._nvl(fee, 'cost', 0.0),
                rate=self._nvl(fee, 'rate', 0.0),
            )
        else:
            return None

    @staticmethod
    def _nvl(dic: Dict, key: str, default_value: Any) -> Any:
        try:
            return dic[key]
        except KeyError:
            return default_value

    def _map_trades(self, trades) -> List[Trade]:
        lst = []
        if not trades:
            return lst
        for trade in trades:
            lst.append(self._map_trade(trade))
        return lst

    def _map_trade(self, trade) -> Trade:
        return Trade(
            id=trade['id'],
            timestamp=trade['timestamp'],
            taker_or_maker=TakerOrMaker(trade['takerOrMaker']),
            price=trade['price'],
            cost=trade['cost'],
            fee=self._map_fee(trade['fee']),
            info=trade['info'],
        )

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
            bot_config: BotConfig,
            id: str,
            params: Dict = {}
    ) -> Order:
        try:
            _conn = common_cctx.connect(exchange, self._logger)
            _order = _conn.fetch_order(
                id=id,
                symbol=str(bot_config.pair),
                params=params
            )
            result = self._map_order(exchange, bot_config, bot_config.pair, _order)
            return result
        except Exception as err:
            raise err
