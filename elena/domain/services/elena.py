from datetime import datetime
from typing import Dict

from elena.domain.model.strategy_config import StrategyConfig
from elena.domain.ports.bot_manager import BotManager
from elena.domain.ports.exchange_manager import ExchangeManager
from elena.domain.ports.logger import Logger
from elena.domain.services.config_loader import ConfigLoader
from elena.domain.services.strategy_manager import StrategyManagerImpl


class Elena:

    def __init__(self,
                 config: Dict,
                 logger: Logger,
                 bot_manager: BotManager,
                 exchange_manager: ExchangeManager,
                 ):
        self._config = config
        self._logger = logger
        self._bot_manager = bot_manager
        self._exchange_manager = exchange_manager
        self._logger.info('Elena initialized')

    def run(self):
        _config_loader = ConfigLoader(self._config)
        _now = datetime.now()
        self._logger.info(f'Starting cycle at %s', _now.isoformat())
        for _strategy_config in _config_loader.strategies:
            self._run_strategy(_config_loader, _strategy_config)

    def _run_strategy(self, config_loader: ConfigLoader, strategy_config: StrategyConfig):
        self._logger.info(f'Running strategy %s: %s', strategy_config.id, strategy_config.name)
        _strategy_manager = StrategyManagerImpl(
            strategy_config=strategy_config,
            logger=self._logger,
            bot_manager=self._bot_manager,
            exchange_manager=self._exchange_manager,
            exchanges=config_loader.exchanges
        )
        _previous_statuses = self._bot_manager.load_all(strategy_config)
        _new_statuses = _strategy_manager.run(_previous_statuses)
        self._bot_manager.write_all(_new_statuses)
