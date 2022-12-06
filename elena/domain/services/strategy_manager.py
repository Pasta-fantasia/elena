from typing import Tuple, List

from elena.domain.model.bot_status import BotStatus
from elena.domain.model.order import Order
from elena.domain.model.strategy_config import StrategyConfig
from elena.domain.model.summary import Summary
from elena.domain.model.time_period import TimePeriod
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
                 order_writer: OrderWriter):
        self._config = strategy_config
        self._logger = logger
        self._bot_manager = bot_manager
        self._market_reader = market_reader
        self._order_writer = order_writer

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
        self._market_reader.read(bot_config.pair, TimePeriod.min_1)
        _fake_order = Order(
            bot_id=bot_config.bot_id,
            strategy_id=self._config.strategy_id,
            order={},
        )
        _summary, _error = self._order_writer.write(_fake_order)
        if _error.is_present():
            self._logger.error('Error writing order: %s', _error.message)
            _status = BotStatus(
                bot_id=bot_config.bot_id,
                status={'error': _error.message},
            )
            return _status, _summary

        _status = BotStatus(
            bot_id=bot_config.bot_id,
            status={},
        )
        return _status, _summary
