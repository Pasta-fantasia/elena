from typing import Protocol, runtime_checkable

from elena.domain.model.bot_status import BotStatus
from elena.domain.ports.logger import Logger


class StorageError(Exception):
    pass


@runtime_checkable
class StorageManager(Protocol):
    def init(self, config: dict, logger: Logger):
        ...

    def load_bot_status(self, bot_id: str) -> BotStatus:
        """Load bot status from storage, raise StorageError on failure"""
        ...

    def save_bot_status(self, status: BotStatus):
        """Save bot status to storage, raise StorageError on failure"""
        ...
