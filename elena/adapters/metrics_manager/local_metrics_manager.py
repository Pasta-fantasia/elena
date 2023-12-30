import pandas as pd

from elena.domain.model.bot_config import BotConfig
from elena.domain.ports.logger import Logger
from elena.domain.ports.metrics_manager import Metric, MetricsManager
from elena.domain.ports.storage_manager import StorageManager


class LocalMetricsManager(MetricsManager):
    _config: dict
    _logger: Logger
    _storage_manager: StorageManager

    def init(self, config: dict, logger: Logger, storage_manager: StorageManager):
        self._config = config
        self._logger = logger
        self._storage_manager = storage_manager

    def counter(self, metric: Metric, bot_config: BotConfig, value: int = 1):
        self._logger.info("'Counter '%s': %s", metric.value, value, bot_config=bot_config)

    def gauge(self, metric: Metric, bot_config: BotConfig, value: float):
        self._logger.info("Gauge '%s': %s", metric.value, value, bot_config=bot_config)

    def candles(self, bot_config: BotConfig, value: pd.DataFrame):
        self._logger.info("Candles: %s", value, bot_config=bot_config)
