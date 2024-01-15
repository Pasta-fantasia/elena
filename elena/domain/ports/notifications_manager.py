from typing import Protocol, runtime_checkable

from elena.domain.ports.logger import Logger
from elena.domain.ports.storage_manager import StorageManager


@runtime_checkable
class NotificationsManager(Protocol):
    def init(self, config: dict, logger: Logger, storage_manager: StorageManager):
        ...

    def high(self, notification: str):
        ...

    def medium(self, notification: str):
        ...

    def low(self, notification: str):
        ...
