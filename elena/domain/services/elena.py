from datetime import datetime
from typing import Dict

from elena.domain.model.strategy_config import StrategyConfig
from elena.domain.ports.bot_manager import BotManager
from elena.domain.ports.exchange_manager import ExchangeManager
from elena.domain.ports.logger import Logger
from elena.domain.ports.metrics_manager import MetricsManager
from elena.domain.ports.notifications_manager import NotificationsManager
from elena.domain.services.config_loader import ConfigLoader
from elena.domain.services.strategy_manager import StrategyManagerImpl


class Elena:
    def __init__(
        self,
        config: Dict,
        logger: Logger,
        metrics_manager: MetricsManager,
        notifications_manager: NotificationsManager,
        bot_manager: BotManager,
        exchange_manager: ExchangeManager,
    ):
        self._config = config
        self._logger = logger
        self._metrics_manager = metrics_manager
        self._notifications_manager = notifications_manager
        self._bot_manager = bot_manager
        self._exchange_manager = exchange_manager
        self._logger.info("Elena initialized")

    def run(self):
        config_loader = ConfigLoader(self._config)
        now = datetime.now()
        self._logger.info("Starting cycle at %s", now.isoformat())
        for _strategy_config in config_loader.strategies:
            self._run_strategy(config_loader, _strategy_config)

    def _run_strategy(self, config_loader: ConfigLoader, strategy_config: StrategyConfig):
        self._logger.info("Running strategy %s: %s", strategy_config.id, strategy_config.name)
        strategy_manager = StrategyManagerImpl(
            strategy_config=strategy_config,
            logger=self._logger,
            metrics_manager=self._metrics_manager,
            notifications_manager=self._notifications_manager,
            bot_manager=self._bot_manager,
            exchange_manager=self._exchange_manager,
            exchanges=config_loader.exchanges,
        )
        previous_statuses = self._bot_manager.load_all(strategy_config)
        new_statuses = strategy_manager.run(previous_statuses)
        self._bot_manager.write_all(new_statuses)
