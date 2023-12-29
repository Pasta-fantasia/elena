import pickle
from os import path
from pathlib import Path

from elena.domain.model.bot_status import BotStatus
from elena.domain.ports.logger import Logger
from elena.domain.ports.storage_manager import StorageError, StorageManager


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
        filename = self._get_bot_status_filename(bot_id)
        self._logger.debug("Loading bot status from disk: %s", filename)
        try:
            with open(filename, "rb") as f:
                status = pickle.load(f)
        except FileNotFoundError as err:
            raise StorageError(f"Error lading bot status {bot_id}: {err}") from err
        self._logger.debug("Loaded bot status %s with %d orders", bot_id, len(status.active_orders))
        return status

    def save_bot_status(self, status: BotStatus):
        """Save bot status to storage, raise StorageError on failure"""
        if not status:
            return
        filename = self._get_bot_status_filename(status.bot_id)
        try:
            self._logger.debug("Saving bot status to disk: %s", filename)
            with open(filename, "wb") as f:
                pickle.dump(status, f, pickle.HIGHEST_PROTOCOL)
        except Exception as err:
            raise StorageError(f"Error saving bot status {status.bot_id}: {err}") from err
        self._logger.debug(
            "Saved bot status %s with %d orders",
            status.bot_id,
            len(status.active_orders),
        )

    def _get_bot_status_filename(self, id: str):
        return path.join(self._path, f"{id}.pickle")
