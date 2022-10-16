import logging
import time
from typing import List, Tuple

from elena.domain.model.bot_status import BotStatus
from elena.domain.model.summary import Summary
from elena.domain.ports.bot_status_manager import BotStatusManager
from elena.domain.ports.config import Config
from elena.domain.ports.emit_flesti import EmitFlesti
from elena.domain.ports.market_reader import MarketReader
from elena.domain.ports.order_writer import OrderWriter
from elena.domain.ports.summary_writer import SummaryWriter
from elena.domain.services.Strategy import Strategy


class Elena:

    def __init__(self,
                 config: Config,
                 emit_flesti: EmitFlesti,
                 bot_status_manager: BotStatusManager,
                 summary_writer: SummaryWriter,
                 market_reader: MarketReader,
                 order_writer: OrderWriter
                 ):
        self._config = config
        self._emit_flesti = emit_flesti
        self._bot_status_manager = bot_status_manager
        self._summary_writer = summary_writer
        self._market_reader = market_reader
        self._order_writer = order_writer
        logging.info('Elena initialized')

    def run(self):
        _profile = self._config.get('Common', 'profile')
        logging.info(f'Starting Elena on {_profile} profile.')

        for start_time in self._emit_flesti:
            self._run_cycle(start_time)

    def _run_cycle(self, start_time: float):
        logging.info(f'Starting cycle at %s (%f)', time.asctime(time.localtime(start_time)), start_time)
        for _strategy_config in self._config.get_strategies():
            _strategy = Strategy(_strategy_config, self._emit_flesti, self._bot_status_manager, self._market_reader,
                                 self._order_writer)
            _result = _strategy.run()
            self._write_strategy_result(_result)

    def _write_strategy_result(self, result: List[Tuple[BotStatus, Summary]]):
        for _tuple in result:
            _err = self._bot_status_manager.write(_tuple[0])
            if _err.is_present():
                raise RuntimeError(_err.message)

            _err = self._summary_writer.write(_tuple[1])
            if _err.is_present():
                raise RuntimeError(_err.message)
