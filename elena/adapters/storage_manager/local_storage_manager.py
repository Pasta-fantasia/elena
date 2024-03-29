from os import path
from pathlib import Path

from elena.adapters.storage_manager.file_storage_manager import FileStorageManager
from elena.domain.ports.logger import Logger


class LocalStorageManager(FileStorageManager):
    _path: str

    def init(self, config: dict, logger: Logger):
        self._logger = logger
        self._path = path.join(config["home"], config["StorageManager"]["path"])
        Path(self._path).mkdir(parents=True, exist_ok=True)
        self._logger.info("LocalStorageManager working at %s", self._path)

    def _get_filepath(self, file_path: str, file_name: str, extension: str = "json") -> str:
        dir_path = path.join(self._path, file_path)
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        return path.join(dir_path, f"{file_name}.{extension}")

    def _load_file(self, filepath: str) -> str:
        with open(filepath) as reader:
            json_data = reader.read()
        return json_data

    def _save_file(self, filepath: str, json_data: str):
        with open(filepath, "w") as writer:
            writer.write(json_data)

    def _delete_file(self, filepath: str):
        Path(filepath).unlink()

    def _append_to_file(self, filepath: str, json_data: str):
        with open(filepath, "a") as writer:
            writer.write(json_data + "\n")
