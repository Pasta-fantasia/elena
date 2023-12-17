from elena.domain.ports.logger import Logger
from elena.domain.ports.notifications_manager import NotificationsManager


class LocalNotificationsManager(NotificationsManager):
    _config: dict
    _logger: Logger

    def init(self, config: dict, logger: Logger):
        self._config = config
        self._logger = logger

    def high(self, notification: str, **kwargs):
        self._logger.info("High notification '%s'", notification, **kwargs)

    def medium(self, notification: str, **kwargs):
        self._logger.info("Medium notification '%s'", notification, **kwargs)

    def low(self, notification: str, **kwargs):
        self._logger.info("Low notification '%s'", notification, **kwargs)
