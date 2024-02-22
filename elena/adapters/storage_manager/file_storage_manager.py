import json
import time
from abc import abstractmethod
from typing import Any, Dict, Optional, Union, List

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

    def _load(self, data_id: str, class_name: str) -> Optional[Any]:
        filepath = self._get_filepath(file_path=class_name, file_name=data_id)
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
            _class = get_class(f"{record.class_module}.{record.class_name}")
            return _class.parse_obj(record.value)
        except Exception as err:
            raise StorageError(f"Error deserializing {record.class_name} {record.id}: {err}") from err

    def save_bot_status(self, bot_status: BotStatus):
        """Insert or overwrite a bot status into storage, raise StorageError on failure"""
        self._save(bot_status.bot_id, bot_status)

    def _save(self, data_id: str, data: Any):
        record = self._to_record(data_id, data)
        record_dict = record.dict()
        json_data = json.dumps(record_dict, indent=4)
        filepath = self._get_filepath(file_path=record.class_name, file_name=data_id)
        self._logger.debug("Saving %s %s to storage: %s", record.class_name, data_id, filepath)
        try:
            self._save_file(filepath, json_data)
        except Exception as err:
            raise StorageError(f"Error saving object {record.class_name} {data_id}: {err}") from err

    @staticmethod
    def _to_record(data_id: str, data: Any, name: Optional[str] = None) -> Record:
        if isinstance(data, pydantic.BaseModel):
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

    def delete_bot_status(self, bot_id: str):
        """Delete a bot status from storage, raise StorageError on failure"""
        self._delete(bot_id, "BotStatus")

    def _delete(self, data_id: str, class_name: str):
        filepath = self._get_filepath(file_path=class_name, file_name=data_id)
        self._logger.debug("Deleting %s %s from storage: %s", class_name, data_id, filepath)
        try:
            self._delete_file(filepath)
        except Exception as err:
            raise StorageError(f"Error deleting BotStatus {class_name} {data_id}: {err}") from err

    def append_metric(self, bot_id: str, metric_name: str, metric_type: str, value: Union[int, float], tags: List[str]):
        data = {
            "timestamp": self._get_time(),
            "bot_id": bot_id,
            "metric_name": metric_name,
            "metric_type": metric_type,
            "value": value,
            "tags": "#".join(tags) or "",
        }
        json_data = json.dumps(data, separators=(",", ":"))
        today = time.strftime("%y%m%d")
        filepath = self._get_filepath(
            file_path=f"Metric/{bot_id}",
            file_name=today,
            extension="jsonl",
        )
        try:
            self._append_to_file(filepath, json_data)
        except Exception as err:
            raise StorageError(f"Error appending Metric {metric_name} {bot_id}: {err}") from err

    @staticmethod
    def _get_time():
        return int(time.time() * 1000)

    @abstractmethod
    def _get_filepath(self, file_path: str, file_name: str, extension: str = "json") -> str:
        ...

    @abstractmethod
    def _load_file(self, filepath: str) -> str:
        ...

    @abstractmethod
    def _save_file(self, filepath: str, json_data: str):
        ...

    @abstractmethod
    def _delete_file(self, filepath: str):
        ...

    @abstractmethod
    def _append_to_file(self, filepath: str, json_data: str):
        ...
