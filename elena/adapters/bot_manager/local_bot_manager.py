from typing import Dict, List

from elena.domain.model.bot_status import BotStatus
from elena.domain.model.strategy_config import StrategyConfig
from elena.domain.ports.bot_manager import BotManager
from elena.domain.ports.logger import Logger
from elena.domain.ports.metrics_manager import MetricsManager
from elena.domain.ports.notifications_manager import NotificationsManager
from elena.domain.ports.storage_manager import StorageError, StorageManager


class LocalBotManager(BotManager):
    _logger: Logger
    _metrics_manager: MetricsManager
    _notifications_manager: NotificationsManager
    _storage_manager: StorageManager

    def init(
        self,
        config: Dict,
        logger: Logger,
        metrics_manager: MetricsManager,
        notifications_manager: NotificationsManager,
        storage_manager: StorageManager,
    ):
        self._logger = logger
        self._metrics_manager = metrics_manager
        self._notifications_manager = notifications_manager
        self._storage_manager = storage_manager

    def load_all(self, strategy_config: StrategyConfig) -> List[BotStatus]:
        statuses = []
        for bot in strategy_config.bots:
            try:
                status = self._storage_manager.load_bot_status(bot.id)
            except StorageError as err:
                self._logger.warning(f"Failed to load bot status for bot {bot.id}: {err}")
                continue
            if status:
                statuses.append(status)
        return statuses

    def save_all(self, statuses: List[BotStatus]):
        for status in statuses:
            try:
                self._storage_manager.save_bot_status(status)
            except StorageError as err:
                self._logger.error(f"Failed to save bot status for bot {status.bot_id}: {err}")
                continue
