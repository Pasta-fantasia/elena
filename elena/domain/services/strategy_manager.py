from typing import List, Optional

from elena.domain.model.bot_config import BotConfig
from elena.domain.model.bot_status import BotStatus
from elena.domain.model.exchange import Exchange, ExchangeType
from elena.domain.model.order import OrderType, OrderSide, Order
from elena.domain.model.strategy_config import StrategyConfig
from elena.domain.ports.bot_manager import BotManager
from elena.domain.ports.exchange_manager import ExchangeManager
from elena.domain.ports.logger import Logger


class StrategyManager:

    def __init__(self,
                 strategy_config: StrategyConfig,
                 logger: Logger,
                 bot_manager: BotManager,
                 exchange_manager: ExchangeManager,
                 exchanges: List[Exchange],
                 ):
        self._config = strategy_config
        self._logger = logger
        self._bot_manager = bot_manager
        self._exchange_manager = exchange_manager
        self._exchanges = exchanges

    def run(self, statuses: List[BotStatus]) -> List[BotStatus]:
        """
        Runs all strategy bots. A Bot is an instance of a strategy with a certain configuration
          1. retrieves the bot status of the previous execution with BotManager
          2. read info from market to define orders with ExchangeManager
          3. write orders to an Exchange with OrderManager
        :param statuses: the list of all bot statuses from previous execution
        :return: the updated list of all bot statuses
        """
        _statuses_dic = {_status.bot_id: _status for _status in statuses}
        _results = []
        for _bot_config in self._config.bots:
            if _bot_config.id in _statuses_dic:
                _status = _statuses_dic[_bot_config.id]
            else:
                _status = None
            _result = self._run_bot(_status, _bot_config)
            _results.append(_result)
        return _results

    def _run_bot(self, status: Optional[BotStatus], bot_config: BotConfig) -> BotStatus:
        _exchange = self._get_exchange(bot_config.exchange_id)
        _candles = self._exchange_manager.read_candles(_exchange, bot_config.pair)
        _order_book = self._exchange_manager.read_order_book(_exchange, bot_config.pair)
        _balance = self._exchange_manager.get_balance(_exchange)
        _order = self._place_order(_exchange, bot_config)
        if status:
            status.orders.append(_order)
        else:
            status = BotStatus(
                bot_id=bot_config.id,
                orders=[_order]
            )
        self._cancel_order(_exchange, bot_config, _order.id)
        return status

    def _get_exchange(self, exchange_id: ExchangeType) -> Exchange:
        for exchange in self._exchanges:
            if exchange.id == exchange_id.value:
                return exchange

    def _place_order(self, exchange: Exchange, bot_config: BotConfig) -> Order:
        _order = self._exchange_manager.place_order(
            exchange=exchange,
            bot_config=bot_config,
            type=OrderType.limit,
            side=OrderSide.buy,
            amount=0.001,
            price=10_000
        )
        self._logger.info('Placed order: %s', _order)
        return _order

    def _fetch_orders(self, exchange: Exchange, bot_config: BotConfig, bot_status: BotStatus) -> List[Order]:
        _orders = []
        for order in bot_status.orders:
            _order = self._exchange_manager.fetch_order(
                exchange=exchange,
                bot_config=bot_config,
                id=order.id,
            )
            _orders.append(_order)
        self._logger.info('Fetched orders: %s', _orders)
        return _orders

    def _cancel_order(self, exchange: Exchange, bot_config: BotConfig, id: str) -> Order:
        _order = self._exchange_manager.cancel_order(
            exchange=exchange,
            bot_config=bot_config,
            id=id
        )
        self._logger.info('Canceled order: %s', id)
        return _order
