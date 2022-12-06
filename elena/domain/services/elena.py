from datetime import datetime
from typing import List, Tuple, Dict

from elena.domain.model.bot_status import BotStatus
from elena.domain.model.summary import Summary
from elena.domain.ports.bot_manager import BotManager
from elena.domain.ports.logger import Logger
from elena.domain.ports.market_reader import MarketReader
from elena.domain.ports.order_writer import OrderWriter
from elena.domain.services.config_loader import ConfigLoader
from elena.domain.services.strategy_manager import StrategyManager


class Elena:

    def __init__(self,
                 config: Dict,
                 logger: Logger,
                 bot_manager: BotManager,
                 market_reader: MarketReader,
                 order_writer: OrderWriter
                 ):
        self._config = config
        self._logger = logger
        self._bot_manager = bot_manager
        self._market_reader = market_reader
        self._order_writer = order_writer
        self._logger.info('Elena initialized')

    def run(self):
        config_loader = ConfigLoader(self._config)
        _now = datetime.now()
        self._logger.info(f'Starting cycle at %s', _now.isoformat())
        for _strategy_config in config_loader.strategies:
            _strategy_manager = StrategyManager(
                _strategy_config,
                self._logger,
                self._bot_manager,
                self._market_reader,
                self._order_writer
            )
            _result = _strategy_manager.run()
            self._write_strategy_result(_result)

    def _write_strategy_result(self, result: List[Tuple[BotStatus, Summary]]):
        for _tuple in result:
            _err = self._bot_manager.write(_tuple[0])
            if _err.is_present():
                raise RuntimeError(_err.message)
