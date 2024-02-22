from typing import List

from elena.domain.ports.logger import Logger
from elena.domain.ports.metrics_manager import MetricsManager
from elena.domain.ports.storage_manager import StorageManager


class LocalMetricsManager(MetricsManager):
    _config: dict
    _logger: Logger
    _storage_manager: StorageManager

    def init(self, config: dict, logger: Logger, storage_manager: StorageManager):
        self._config = config
        self._logger = logger
        self._storage_manager = storage_manager

    def counter(self, metric: str, bot_id: str, value: int, tags: List[str]):
        self._storage_manager.append_metric(bot_id, metric, "counter", value, tags)

    def gauge(self, metric: str, bot_id: str, value: float, tags: List[str]):
        self._storage_manager.append_metric(bot_id, metric, "gauge", value, tags)
