from typing import Protocol

from elena.domain.ports.logger import Logger


class NotificationsManager(Protocol):
    def init(self, config: dict, logger: Logger):
        ...

    def high(self, notification: str, **kwargs):
        ...

    def medium(self, notification: str, **kwargs):
        ...

    def low(self, notification: str, **kwargs):
        ...
