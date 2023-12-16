from elena.domain.ports.logger import Logger
from elena.domain.ports.metrics_manager import MetricsManager


class LocalMetricsManager(MetricsManager):
    _config: dict
    _logger: Logger

    def init(self, config: dict, logger: Logger):
        self._config = config
        self._logger = logger

    def counter(self, name, value, **kwargs):
        self._logger.info("Counter %s: %s", name, value, **kwargs)

    def histogram(self, name, value, **kwargs):
        self._logger.info("Histogram %s: %s", name, value, **kwargs)
