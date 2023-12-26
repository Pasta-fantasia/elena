from typing import Protocol, runtime_checkable

from elena.domain.ports.logger import Logger


@runtime_checkable
class NotificationsManager(Protocol):
    def init(self, config: dict, logger: Logger):
        ...

    def high(self, notification: str):
        ...

    def medium(self, notification: str):
        ...

    def low(self, notification: str):
        ...
