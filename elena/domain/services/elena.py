import os
from datetime import datetime
from typing import Dict

from elena.domain.model.strategy_config import StrategyConfig
from elena.domain.ports.bot_manager import BotManager
from elena.domain.ports.config_manager import ConfigManager
from elena.domain.ports.exchange_manager import ExchangeManager
from elena.domain.ports.logger import Logger
from elena.domain.ports.metrics_manager import MetricsManager
from elena.domain.ports.notifications_manager import NotificationsManager
from elena.domain.ports.storage_manager import StorageManager
from elena.domain.services.config_loader import ConfigLoader
from elena.domain.services.strategy_manager import StrategyManagerImpl
from elena.shared.dynamic_loading import get_class


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
        self._config_loader = ConfigLoader(self._config, self._logger)
        self._logger.info("Elena initialized")

    def run(self):
        now = datetime.now()
        self._logger.info("Starting cycle at %s", now.isoformat())
        for _strategy_config in self._config_loader.strategies:
            self._run_strategy(_strategy_config)

    def _run_strategy(self, strategy_config: StrategyConfig):
        if not strategy_config.enabled:
            self._logger.info("Skipping strategy %s: %s", strategy_config.id, strategy_config.name)
            return
        self._logger.info("Running strategy %s: %s", strategy_config.id, strategy_config.name)
        strategy_manager = StrategyManagerImpl(
            strategy_config=strategy_config,
            logger=self._logger,
            metrics_manager=self._metrics_manager,
            notifications_manager=self._notifications_manager,
            bot_manager=self._bot_manager,
            exchange_manager=self._exchange_manager,
            exchanges=self._config_loader.exchanges,
        )
        previous_statuses = self._bot_manager.load_all(strategy_config)
        new_statuses = strategy_manager.run(previous_statuses)
        self._bot_manager.save_all(new_statuses)


def get_config_manager(config_manager_class_path: str, config_manager_url: str) -> ConfigManager:
    config_manager_class = get_class(config_manager_class_path)
    if not issubclass(config_manager_class, ConfigManager):
        raise ValueError(f"{config_manager_class_path} must implement ConfigManager")
    config_manager = config_manager_class()
    config_manager.init(config_manager_url)
    return config_manager


def get_logger(config: Dict) -> Logger:
    logger_class = get_class(config["Logger"]["class"])
    if not issubclass(logger_class, Logger):
        raise ValueError(f'{config["Logger"]["class"]} must implement Logger')
    logger = logger_class()
    logger.init(config)
    return logger


def get_storage_manager(config: Dict, logger: Logger) -> StorageManager:
    storage_manager_class = get_class(config["StorageManager"]["class"])
    if not issubclass(storage_manager_class, StorageManager):
        raise ValueError(f'{config["StorageManager"]["class"]} must implement StorageManager')
    storage_manager = storage_manager_class()
    storage_manager.init(config, logger)
    return storage_manager


def get_metrics_manager(config: Dict, logger: Logger, storage_manager: StorageManager) -> MetricsManager:
    metrics_manager_class = get_class(config["MetricsManager"]["class"])
    if not issubclass(metrics_manager_class, MetricsManager):
        raise ValueError(f'{config["MetricsManager"]["class"]} must implement MetricsManager')
    metrics_manager = metrics_manager_class()
    metrics_manager.init(config, logger, storage_manager)
    return metrics_manager


def get_bot_manager(config: Dict, logger: Logger, storage_manager: StorageManager) -> BotManager:
    bot_manager_class = get_class(config["BotManager"]["class"])
    if not issubclass(bot_manager_class, BotManager):
        raise ValueError(f'{config["BotManager"]["class"]} must implement BotManager')
    bot_manager = bot_manager_class()
    bot_manager.init(
        config=config,
        logger=logger,
        storage_manager=storage_manager,
    )
    return bot_manager


def get_notifications_manager(config: Dict, logger: Logger, storage_manager: StorageManager) -> NotificationsManager:
    notifications_manager_class = get_class(config["NotificationsManager"]["class"])
    if not issubclass(notifications_manager_class, NotificationsManager):
        raise ValueError(f'{config["NotificationsManager"]["class"]} must implement NotificationsManager')
    notifications_manager = notifications_manager_class()
    notifications_manager.init(config, logger, storage_manager)
    return notifications_manager


def get_exchange_manager(config: Dict, logger: Logger, storage_manager: StorageManager) -> ExchangeManager:
    exchange_manager_class = get_class(config["ExchangeManager"]["class"])
    if not issubclass(exchange_manager_class, ExchangeManager):
        raise ValueError(f'{config["ExchangeManager"]["class"]} must implement ExchangeManager')
    exchange_manager = exchange_manager_class()
    exchange_manager.init(
        config=config,
        logger=logger,
        storage_manager=storage_manager,
    )
    return exchange_manager


def get_elena_instance(config_manager_class_path: str = "elena.adapters.config.local_config_manager.LocalConfigManager", config_manager_url: str = "") -> Elena:
    if config_manager_url == "":
        config_manager_url = os.environ.get("ELENA_HOME", os.getcwd())

    config_manager = get_config_manager(config_manager_class_path, config_manager_url)
    config = config_manager.get_config()
    logger = get_logger(config)
    storage_manager = get_storage_manager(config, logger)
    metrics_manager = get_metrics_manager(config, logger, storage_manager)
    notifications_manager = get_notifications_manager(config, logger, storage_manager)
    bot_manager = get_bot_manager(config, logger, storage_manager)
    exchange_manager = get_exchange_manager(config, logger, storage_manager)

    return Elena(
        config=config,
        logger=logger,
        metrics_manager=metrics_manager,
        notifications_manager=notifications_manager,
        bot_manager=bot_manager,
        exchange_manager=exchange_manager,
    )
