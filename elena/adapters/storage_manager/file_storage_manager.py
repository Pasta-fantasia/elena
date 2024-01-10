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


class FileStorageManager(StorageManager):
    _logger: Logger

    @abstractmethod
    def init(self, config: dict, logger: Logger):
        ...

    def load_bot_status(self, bot_id: str) -> BotStatus:
        """Load bot status from storage, raise StorageError on failure"""
        return self._load(bot_id, "BotStatus")  # type: ignore

    def save_bot_status(self, bot_status: BotStatus):
        """Inserts or updates bot status to storage, raise StorageError on failure"""
        self._save(bot_status.bot_id, bot_status)

    def delete_bot_status(self, bot_id: str):
        """Delete bot status from storage, raise StorageError on failure"""
        self._delete(bot_id, "BotStatus")

    def load_data_frame(self, df_id: str) -> pd.DataFrame:
        """Load Pandas DataFrame from storage, raise StorageError on failure"""
        return self._load(df_id, "DataFrame")  # type: ignore

    def save_data_frame(self, df_id: str, df: pd.DataFrame):
        """Save Pandas DataFrame to storage, raise StorageError on failure"""
        try:
            existing_pd = self._load(df_id, "DataFrame")  # type: ignore
        except StorageError:
            existing_pd = pd.DataFrame()

        if existing_pd.empty:  # type: ignore
            self._save(df_id, df)
        else:
            try:
                # Try to merge the existing DataFrame with the new one
                merged_pd = pd.merge(existing_pd, df, how="outer")
                self._save(df_id, merged_pd)
            except pd.errors.MergeError:
                # If the merge fails, just save the new DataFrame
                self._save(df_id, df)

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
                return pd.read_json(record.value)
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
    def _to_record(data_id: str, data: Any) -> Record:
        if isinstance(data, pd.DataFrame):
            value = data.to_json()
        elif isinstance(data, pydantic.BaseModel):
            value = data.dict()
        else:
            raise Exception(f"Un-implemented serialization for type {data.__class__.__name__}")
        return Record(
            id=data_id,
            class_module=data.__class__.__module__,
            class_name=data.__class__.__qualname__,
            value=value,
        )

    @abstractmethod
    def _save_file(self, filepath: str, json_data: str):
        ...

    @abstractmethod
    def _get_filepath(self, data_id: str, class_name: str) -> Any:
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
