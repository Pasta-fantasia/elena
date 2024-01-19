from typing import Protocol, runtime_checkable, Union, List

from elena.domain.model.bot_status import BotStatus
from elena.domain.ports.logger import Logger


class StorageError(Exception):
    pass


@runtime_checkable
class StorageManager(Protocol):
    def init(self, config: dict, logger: Logger):
        ...

    def load_bot_status(self, bot_id: str) -> BotStatus:
        """Load a bot status from storage, raise StorageError on failure"""
        ...

    def save_bot_status(self, bot_status: BotStatus):
        """Insert or overwrite a bot status into storage, raise StorageError on failure"""
        ...

    def delete_bot_status(self, bot_id: str):
        """Delete a bot status from storage, raise StorageError on failure"""
        ...

    def append_metric(self, bot_id: str, metric_name: str, metric_type: str, value: Union[int, float], tags: List[str]):
        ...
