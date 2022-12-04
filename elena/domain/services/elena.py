import logging
from datetime import datetime
from typing import List, Tuple

from elena.domain.model.bot_status import BotStatus
from elena.domain.model.summary import Summary
from elena.domain.ports.bot_status_manager import BotStatusManager
from elena.domain.ports.config import Config
from elena.domain.ports.market_reader import MarketReader
from elena.domain.ports.order_writer import OrderWriter
from elena.domain.services.Strategy import Strategy


class Elena:

    def __init__(self,
                 config: Config,
                 bot_status_manager: BotStatusManager,
                 market_reader: MarketReader,
                 order_writer: OrderWriter
                 ):
        self._config = config
        self._bot_status_manager = bot_status_manager
        self._market_reader = market_reader
        self._order_writer = order_writer
        logging.info('Elena initialized')

    def run(self):
        _now = datetime.now()
        logging.info(f'Starting cycle at %s', _now.isoformat())
        for _strategy_config in self._config.get_strategies():
            _strategy = Strategy(_strategy_config, self._bot_status_manager, self._market_reader,
                                 self._order_writer)
            _result = _strategy.run()
            self._write_strategy_result(_result)

    def _write_strategy_result(self, result: List[Tuple[BotStatus, Summary]]):
        for _tuple in result:
            _err = self._bot_status_manager.write(_tuple[0])
            if _err.is_present():
                raise RuntimeError(_err.message)
