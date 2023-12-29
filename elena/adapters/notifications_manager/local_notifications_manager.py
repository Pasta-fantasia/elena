from elena.domain.ports.logger import Logger
from elena.domain.ports.notifications_manager import NotificationsManager
from elena.domain.ports.storage_manager import StorageManager


class LocalNotificationsManager(NotificationsManager):
    _config: dict
    _logger: Logger
    _storage_manager: StorageManager

    def init(self, config: dict, logger: Logger, storage_manager: StorageManager):
        self._config = config
        self._logger = logger
        self._storage_manager = storage_manager

    def high(self, notification: str, **kwargs):
        self._logger.info("High notification '%s'", notification, **kwargs)

    def medium(self, notification: str, **kwargs):
        self._logger.info("Medium notification '%s'", notification, **kwargs)

    def low(self, notification: str, **kwargs):
        self._logger.info("Low notification '%s'", notification, **kwargs)
