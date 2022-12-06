from datetime import datetime
from typing import List, Tuple, Dict

from elena.domain.model.bot_config import BotConfig
from elena.domain.model.bot_status import BotStatus
from elena.domain.model.strategy_config import StrategyConfig
from elena.domain.model.summary import Summary
from elena.domain.model.trading_pair import TradingPair
from elena.domain.ports.bot_manager import BotManager
from elena.domain.ports.logger import Logger
from elena.domain.ports.market_reader import MarketReader
from elena.domain.ports.order_writer import OrderWriter
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
        _now = datetime.now()
        self._logger.info(f'Starting cycle at %s', _now.isoformat())
        for _strategy_config in self._get_strategies():
            _strategy_manager = StrategyManager(
                _strategy_config,
                self._logger,
                self._bot_manager,
                self._market_reader,
                self._order_writer
            )
            _result = _strategy_manager.run()
            self._write_strategy_result(_result)

    def _get_strategies(self) -> List[StrategyConfig]:
        _results = []
        for _dict in self._config['Strategies']:
            _strategy = StrategyConfig(
                strategy_id=_dict['id'],
                name=_dict['name'],
                enabled=_dict['enabled'],
                bots=self._get_bots(_dict['bots'], _dict['id'])
            )
            if _strategy.enabled:
                _results.append(_strategy)
        return _results

    @staticmethod
    def _get_bots(bots: List[Dict], strategy_id: str) -> List[BotConfig]:
        _results = []
        for _dict in bots:
            _bot = BotConfig(
                bot_id=_dict['id'],
                name=_dict['name'],
                strategy_id=strategy_id,
                enabled=_dict['enabled'],
                pair=TradingPair.build(_dict['pair']),
                exchange_id=_dict['exchange'],
                tags=_dict['tags'],
                config=_dict['config'],
            )
            if _bot.enabled:
                _results.append(_bot)
        return _results

    def _write_strategy_result(self, result: List[Tuple[BotStatus, Summary]]):
        for _tuple in result:
            _err = self._bot_manager.write(_tuple[0])
            if _err.is_present():
                raise RuntimeError(_err.message)
