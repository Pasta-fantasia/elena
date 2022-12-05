from datetime import datetime
from typing import List, Tuple

from elena.domain.model.bot_status import BotStatus
from elena.domain.model.summary import Summary
from elena.domain.ports.bot_status_manager import BotSpawner
from elena.domain.ports.config import Config
from elena.domain.ports.logger import Logger
from elena.domain.ports.market_reader import MarketReader
from elena.domain.ports.order_writer import OrderWriter
from elena.domain.services.Strategy import Strategy


class Elena:

    def __init__(self,
                 config: Config,
                 logger: Logger,
                 bot_spawner: BotSpawner,
                 market_reader: MarketReader,
                 order_writer: OrderWriter
                 ):
        self._config = config
        self._logger = logger
        self._bot_spawner = bot_spawner
        self._market_reader = market_reader
        self._order_writer = order_writer
        self._logger.info('Elena initialized')

    def run(self):
        _now = datetime.now()
        self._logger.info(f'Starting cycle at %s', _now.isoformat())
        for _strategy_config in self._config.get_strategies():
            _strategy = Strategy(_strategy_config, self._logger, self._bot_spawner, self._market_reader,
                                 self._order_writer)
            _result = _strategy.run()
            self._write_strategy_result(_result)

    def _write_strategy_result(self, result: List[Tuple[BotStatus, Summary]]):
        for _tuple in result:
            _err = self._bot_spawner.write(_tuple[0])
            if _err.is_present():
                raise RuntimeError(_err.message)
