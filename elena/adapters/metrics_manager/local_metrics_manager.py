import pandas as pd
from domain.model.bot_config import BotConfig

from elena.domain.ports.logger import Logger
from elena.domain.ports.metrics_manager import Metric, MetricsManager


class LocalMetricsManager(MetricsManager):
    _config: dict
    _logger: Logger

    def init(self, config: dict, logger: Logger):
        self._config = config
        self._logger = logger

    def counter(self, metric: Metric, bot_config: BotConfig, value: int = 1):
        self._logger.info("'Counter '%s': %s", metric.value, value, bot_config=bot_config)

    def gauge(self, metric: Metric, bot_config: BotConfig, value: float):
        self._logger.info("Gauge '%s': %s", metric.value, value, bot_config=bot_config)

    def candles(self, bot_config: BotConfig, value: pd.DataFrame):
        self._logger.info("Candles: %s", value, bot_config=bot_config)
