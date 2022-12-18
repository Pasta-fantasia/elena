from datetime import datetime
from typing import List, Tuple, Dict

from elena.domain.model.bot_status import BotStatus
from elena.domain.model.summary import Summary
from elena.domain.ports.bot_manager import BotManager
from elena.domain.ports.exchange_reader import ExchangeReader
from elena.domain.ports.logger import Logger
from elena.domain.ports.order_manager import OrderManager
from elena.domain.services.config_loader import ConfigLoader
from elena.domain.services.strategy_manager import StrategyManager


class Elena:

    def __init__(self,
                 config: Dict,
                 logger: Logger,
                 bot_manager: BotManager,
                 exchange_reader: ExchangeReader,
                 order_manager: OrderManager
                 ):
        self._config = config
        self._logger = logger
        self._bot_manager = bot_manager
        self._exchange_reader = exchange_reader
        self._order_manager = order_manager
        self._logger.info('Elena initialized')

    def run(self):
        config_loader = ConfigLoader(self._config)
        _now = datetime.now()
        self._logger.info(f'Starting cycle at %s', _now.isoformat())
        for _strategy_config in config_loader.strategies:
            _strategy_manager = StrategyManager(
                strategy_config=_strategy_config,
                logger=self._logger,
                bot_manager=self._bot_manager,
                exchange_reader=self._exchange_reader,
                order_manager=self._order_manager,
                exchanges=config_loader.exchanges
            )
            _result = _strategy_manager.run()
            self._write_strategy_result(_result)

    def _write_strategy_result(self, result: List[Tuple[BotStatus, Summary]]):
        for _tuple in result:
            self._write_bot_status(_tuple[0])

    def _write_bot_status(self, status: BotStatus):
        try:
            self._bot_manager.write(status)
        except Exception as _err:
            raise _err
