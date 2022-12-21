import time
from typing import List

from elena.domain.model.bot_config import BotConfig
from elena.domain.model.bot_status import BotStatus
from elena.domain.model.exchange import Exchange, ExchangeType
from elena.domain.model.order import OrderType, OrderSide, Order
from elena.domain.model.strategy_config import StrategyConfig
from elena.domain.ports.bot_manager import BotManager
from elena.domain.ports.exchange_reader import ExchangeReader
from elena.domain.ports.logger import Logger
from elena.domain.ports.order_manager import OrderManager


class StrategyManager:

    def __init__(self,
                 strategy_config: StrategyConfig,
                 logger: Logger,
                 bot_manager: BotManager,
                 exchange_reader: ExchangeReader,
                 order_manager: OrderManager,
                 exchanges: List[Exchange],
                 ):
        self._config = strategy_config
        self._logger = logger
        self._bot_manager = bot_manager
        self._exchange_reader = exchange_reader
        self._order_manager = order_manager
        self._exchanges = exchanges

    def run(self) -> List[BotStatus]:
        """
        Runs all strategy bots. A Bot is an instance of a strategy with a certain configuration
          1. retrieves the bot status of the previous execution with BotManager
          2. read info from market to define orders with ExchangeReader
          3. write orders to an Exchange with OrderManager
        :return: the list of all bot status of this execution
        """
        _results = []
        for bot_config in self._config.bots:
            _result = self._run_bot(bot_config)
            _results.append(_result)
        return _results

    def _run_bot(self, bot_config: BotConfig) -> BotStatus:
        _exchange = self._get_exchange(bot_config.exchange_id)
        # _candles = self._exchange_reader.read_candles(_exchange, bot_config.pair)
        # _order_book = self._exchange_reader.read_order_book(_exchange, bot_config.pair)
        # _balance = self._exchange_reader.get_balance(_exchange)
        _order = self._place_order(_exchange, bot_config)
        time.sleep(2)
        _status = BotStatus(
            config=bot_config,
            orders=[_order],
        )
        self._fetch_orders(_exchange, _status)
        time.sleep(2)
        self._cancel_order(_exchange, bot_config, _order.id)
        return _status

    def _get_exchange(self, exchange_id: ExchangeType) -> Exchange:
        for exchange in self._exchanges:
            if exchange.id == exchange_id.value:
                return exchange

    def _place_order(self, exchange: Exchange, bot_config: BotConfig) -> Order:
        _order = self._order_manager.place(
            exchange=exchange,
            bot_config=bot_config,
            type=OrderType.limit,
            side=OrderSide.buy,
            amount=0.001,
            price=20_000
        )
        self._logger.info('Placed order: %s', _order)
        return _order

    def _fetch_orders(self, exchange: Exchange, bot_status: BotStatus) -> List[Order]:
        _orders = []
        for order in bot_status.orders:
            _order = self._order_manager.fetch(
                exchange=exchange,
                bot_config=bot_status.config,
                id=order.id,
            )
            _orders.append(_order)
        self._logger.info('Fetched orders: %s', _orders)
        return _orders

    def _cancel_order(self, exchange: Exchange, bot_config: BotConfig, id: str) -> Order:
        _order = self._order_manager.cancel(
            exchange=exchange,
            bot_config=bot_config,
            id=id
        )
        self._logger.info('Canceled order: %s', id)
        return _order
