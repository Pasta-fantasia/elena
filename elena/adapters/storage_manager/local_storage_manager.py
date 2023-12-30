import json
from os import path
from pathlib import Path
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


class LocalStorageManager(StorageManager):
    _config: dict
    _logger: Logger
    _path: str

    def init(self, config: dict, logger: Logger):
        self._config = config
        self._logger = logger
        self._path = path.join(config["home"], config["StorageManager"]["path"])
        Path(self._path).mkdir(parents=True, exist_ok=True)
        logger.info("LocalStorageManager working at %s", self._path)

    def load_bot_status(self, bot_id: str) -> BotStatus:
        """Load bot status from storage, raise StorageError on failure"""
        return self._load(bot_id, "BotStatus")  # type: ignore

    def save_bot_status(self, bot_status: BotStatus):
        """Save bot status to storage, raise StorageError on failure"""
        self._save(bot_status.bot_id, bot_status)

    def _load(self, data_id: str, class_name: str) -> Optional[Any]:
        filepath = self._get_filepath(data_id, class_name)
        self._logger.debug("Loading %s %s from disk: %s", class_name, data_id, filepath)
        try:
            with open(filepath, "r") as fp:
                record_dict = json.load(fp)
                record = Record.parse_obj(record_dict)
            return self._from_record(record)
        except Exception as err:
            raise StorageError(f"Error loading {class_name} {data_id}: {err}") from err

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

    def _save(self, data_id: str, data: Any):
        record = self._to_record(data_id, data)
        filepath = self._get_filepath(data_id, record.class_name)
        self._logger.debug("Saving %s %s to disk: %s", record.class_name, data_id, filepath)
        try:
            with open(filepath, "w") as fp:
                record_dict = record.dict()
                json.dump(record_dict, fp, indent=4)
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

    def _get_filepath(self, data_id: str, class_name: str) -> Any:
        dir_path = path.join(self._path, class_name)
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        return path.join(dir_path, f"{data_id}.json")
