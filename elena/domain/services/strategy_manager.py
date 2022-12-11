from typing import Tuple, List

from elena.domain.model.bot_status import BotStatus
from elena.domain.model.exchange import Exchange, ExchangeType
from elena.domain.model.order import Order
from elena.domain.model.strategy_config import StrategyConfig
from elena.domain.model.summary import Summary
from elena.domain.model.time_frame import TimeFrame
from elena.domain.ports.bot_manager import BotManager
from elena.domain.ports.logger import Logger
from elena.domain.ports.market_reader import MarketReader
from elena.domain.ports.order_writer import OrderWriter


class StrategyManager:

    def __init__(self,
                 strategy_config: StrategyConfig,
                 logger: Logger,
                 bot_manager: BotManager,
                 market_reader: MarketReader,
                 order_writer: OrderWriter,
                 exchanges: List[Exchange],
                 ):
        self._config = strategy_config
        self._logger = logger
        self._bot_manager = bot_manager
        self._market_reader = market_reader
        self._order_writer = order_writer
        self._exchanges = exchanges

    def run(self) -> List[Tuple[BotStatus, Summary]]:
        """
        Runs all strategy bots. A Bot is an instance of a strategy with a certain configuration
          1. retrieves the bot status of the previous execution with BotManager
          2. read info from market to define orders with MarketReader
          3. write orders to an Exchange with OrderWriter
        :return: the list of all bot status of this execution, and the summary of every execution
        """
        _results = []
        for bot_config in self._config.bots:
            _result = self._run_bot(bot_config)
            _results.append(_result)
        return _results

    def _run_bot(self, bot_config) -> Tuple[BotStatus, Summary]:
        _exchange = self._get_exchange(bot_config.exchange_id)
        _candles = self._market_reader.read_candles(_exchange, bot_config.pair, TimeFrame.min_1)
        _order_book = self._market_reader.read_order_book(_exchange, bot_config.pair)
        return self._write_order(_exchange, bot_config)

    def _write_order(self, exchange: Exchange, bot_config) -> Tuple[BotStatus, Summary]:
        _fake_order = Order(
            _exchange=exchange,
            bot_id=bot_config.id,
            strategy_id=self._config.id,
            order={},
        )
        try:
            _summary = self._order_writer.write(_fake_order)
        except Exception as _error:
            self._logger.error('Error writing order: %s', _error)
            _status = BotStatus(
                bot_id=bot_config.bot_id,
                status={'error': _error},
            )
            _summary = Summary(
                bot_id=bot_config.bot_id,
                strategy_id=self._config.id,
                summanry={'error': _error.__str__()}
            )
            return _status, _summary

        _status = BotStatus(
            bot_id=bot_config.id,
            status={},
        )
        return _status, _summary

    def _get_exchange(self, exchange_id: ExchangeType) -> Exchange:
        for exchange in self._exchanges:
            if exchange.id == exchange_id.value:
                return exchange
