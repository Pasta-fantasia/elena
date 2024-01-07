from os import path
from pathlib import Path
from typing import Any

from elena.adapters.storage_manager.file_storage_manager import \
    FileStorageManager
from elena.domain.ports.logger import Logger


class LocalStorageManager(FileStorageManager):
    _path: str

    def init(self, config: dict, logger: Logger):
        self._logger = logger
        self._path = path.join(config["home"], config["StorageManager"]["path"])
        Path(self._path).mkdir(parents=True, exist_ok=True)
        self._logger.info("LocalStorageManager working at %s", self._path)

    def _get_filepath(self, data_id: str, class_name: str) -> Any:
        dir_path = path.join(self._path, class_name)
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        return path.join(dir_path, f"{data_id}.json")

    def _load_file(self, filepath: str) -> str:
        with open(filepath) as reader:
            json_data = reader.read()
        return json_data

    def _save_file(self, filepath: str, json_data: str):
        with open(filepath, "w") as writer:
            writer.write(json_data)

    def _delete_file(self, filepath: str):
        Path(filepath).unlink()
