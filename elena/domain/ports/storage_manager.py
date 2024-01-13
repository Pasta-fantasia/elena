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
        """Load a bot status from storage, raise StorageError on failure"""
        ...

    def save_bot_status(self, bot_status: BotStatus):
        """Insert or overwrite a bot status into storage, raise StorageError on failure"""
        ...

    def delete_bot_status(self, bot_id: str):
        """Delete a bot status from storage, raise StorageError on failure"""
        ...

    def load_data_frame(self, df_id: str) -> pd.DataFrame:
        """Load a Pandas DataFrame from storage, raise StorageError on failure"""
        ...

    def save_data_frame(self, df_id: str, df: pd.DataFrame):
        """Insert or overwrite a Pandas DataFrame into storage, raise StorageError on failure"""
        ...

    def merge_data_frame(self, df_id: str, df: pd.DataFrame, index_column: str) -> pd.DataFrame:
        """
        Merges an existing Pandas DataFrame with the new one, raise StorageError on failure
        Both DataFrames will be indexed by the same column before merging
        and also have the same columns, and then the new values will be merged with the old ones
        The new values will overwrite the old ones if they have the same index and column
        If there is no existing DataFrame, it will be created
        """
        ...

    def delete_data_frame(self, df_id: str):
        """Delete Pandas DataFrame from storage, raise StorageError on failure"""
        ...
