import json
from abc import abstractmethod
from typing import Any, Dict, Optional, Union

import pandas as pd
import pydantic
from pydantic import BaseModel

from elena.domain.model.bot_status import BotStatus
from elena.domain.ports.logger import Logger
from elena.domain.ports.storage_manager import StorageError, StorageManager
from elena.shared.dynamic_loading import get_class


class Record(BaseModel):
    id: str
    class_name: str
    class_module: str
    value: Union[str, Dict[str, Any]]
    name: str


class FileStorageManager(StorageManager):
    _logger: Logger

    @abstractmethod
    def init(self, config: dict, logger: Logger):
        ...

    def load_bot_status(self, bot_id: str) -> BotStatus:
        """Load bot status from storage, raise StorageError on failure"""
        return self._load(bot_id, "BotStatus")  # type: ignore

    def save_bot_status(self, bot_status: BotStatus):
        """Insert or overwrite a bot status into storage, raise StorageError on failure"""
        self._save(bot_status.bot_id, bot_status)

    def delete_bot_status(self, bot_id: str):
        """Delete a bot status from storage, raise StorageError on failure"""
        self._delete(bot_id, "BotStatus")

    def load_data_frame(self, df_id: str) -> pd.DataFrame:
        """Load a Pandas DataFrame from storage, raise StorageError on failure"""
        return self._load(df_id, "DataFrame")  # type: ignore

    def save_data_frame(self, df_id: str, df: pd.DataFrame):
        """Insert or overwrite a Pandas DataFrame into storage, raise StorageError on failure"""
        self._save(df_id, df)

    def merge_data_frame(self, df_id: str, df: pd.DataFrame, index_column: str) -> pd.DataFrame:
        """
        Merges an existing Pandas DataFrame with the new one, raise StorageError on failure
        Both DataFrames will be indexed by the same column(s) before merging
        and also have the same columns, and then the new values will be merged with the old ones
        The new values will overwrite the old ones if they have the same index and column
        If there is no existing DataFrame, it will be created
        """
        try:
            existing_df: pd.DataFrame = self._load(df_id, "DataFrame")
        except StorageError:
            existing_df = pd.DataFrame()

        if existing_df.empty:  # type: ignore
            self._save(df_id, df)
            return df

        try:
            # Try to merge the existing DataFrame with the new one and save it
            merged_df = pd.concat([existing_df[existing_df[index_column].isin(df[index_column]) == False], df]).reset_index(drop=True)  # noqa: E712
            self._save(df_id, merged_df)
            return merged_df
        except pd.errors.MergeError:
            # If the merge fails, just save the new DataFrame
            self._save(df_id, df)
            return df

    def delete_data_frame(self, df_id: str):
        """Delete Pandas DataFrame from storage, raise StorageError on failure"""
        self._delete(df_id, "DataFrame")

    def _load(self, data_id: str, class_name: str) -> Optional[Any]:
        filepath = self._get_filepath(data_id, class_name)
        self._logger.debug("Loading %s %s from storage: %s", class_name, data_id, filepath)
        try:
            json_data = self._load_file(filepath)
        except Exception as err:
            raise StorageError(f"Error loading {class_name} {data_id}: {err}") from err
        record_dict = json.loads(json_data)
        record = Record.parse_obj(record_dict)
        return self._from_record(record)

    @classmethod
    def _from_record(self, record: Record) -> Any:
        try:
            if record.class_name == "DataFrame":
                return pd.DataFrame.from_dict(record.value)
            else:
                _class = get_class(f"{record.class_module}.{record.class_name}")
                return _class.parse_obj(record.value)
        except Exception as err:
            raise StorageError(f"Error deserializing {record.class_name} {record.id}: {err}") from err

    @abstractmethod
    def _load_file(self, filepath: str) -> str:
        ...

    def _save(self, data_id: str, data: Any):
        record = self._to_record(data_id, data)
        record_dict = record.dict()
        json_data = json.dumps(record_dict, indent=4)
        filepath = self._get_filepath(data_id, record.class_name)
        self._logger.debug("Saving %s %s to storage: %s", record.class_name, data_id, filepath)
        try:
            self._save_file(filepath, json_data)
        except Exception as err:
            raise StorageError(f"Error saving object {record.class_name} {data_id}: {err}") from err

    @staticmethod
    def _to_record(data_id: str, data: Any, name: Optional[str] = None) -> Record:
        if isinstance(data, dict):
            value = data
        elif isinstance(data, pydantic.BaseModel):
            value = data.dict()
        else:
            raise Exception(f"Un-implemented serialization for type {data.__class__.__name__}")
        return Record(
            id=data_id,
            class_module=data.__class__.__module__,
            class_name=data.__class__.__qualname__,
            value=value,
            name=name or data.__class__.__qualname__,
        )

    @abstractmethod
    def _save_file(self, filepath: str, json_data: str):
        ...

    @abstractmethod
    def _get_filepath(self, data_id: str, class_name: str, extension: str = "json") -> str:
        ...

    def _delete(self, data_id: str, class_name: str):
        """Delete bot status from storage, raise StorageError on failure"""
        filepath = self._get_filepath(data_id, class_name)
        self._logger.debug("Deleting %s %s from storage: %s", class_name, data_id, filepath)
        try:
            self._delete_file(filepath)
        except Exception as err:
            raise StorageError(f"Error deleting BotStatus {class_name} {data_id}: {err}") from err

    @abstractmethod
    def _delete_file(self, filepath: str):
        ...

    @abstractmethod
    def _append_to_file(self, filepath: str, json_data: str):
        ...
