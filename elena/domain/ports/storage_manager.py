from typing import Protocol, runtime_checkable

import pandas as pd

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

    def save_bot_status(self, bot_status: BotStatus):
        """Insert or update bot status into storage, raise StorageError on failure"""
        ...

    def delete_bot_status(self, bot_id: str):
        """Delete bot status from storage, raise StorageError on failure"""
        ...

    def load_data_frame(self, df_id: str) -> pd.DataFrame:
        """Load Pandas DataFrame from storage, raise StorageError on failure"""
        ...

    def save_data_frame(self, df_id: str, df: pd.DataFrame):
        """
        Insert or update Pandas DataFrame into storage, raise StorageError on failure
        To update a DataFrame, both DataFrame have to be indexed by the same column(s)
        and also have the same columns, and then the new values will be merged with the old ones
        """
        ...

    def delete_data_frame(self, df_id: str):
        """Delete Pandas DataFrame from storage, raise StorageError on failure"""
        ...
