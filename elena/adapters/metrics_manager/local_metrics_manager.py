from elena.domain.ports.logger import Logger
from elena.domain.ports.metrics_manager import Metric, MetricsManager


class LocalMetricsManager(MetricsManager):
    _config: dict
    _logger: Logger

    def init(self, config: dict, logger: Logger):
        self._config = config
        self._logger = logger

    def counter(self, metric: Metric, value, **kwargs):
        self._logger.info("'Counter '%s': %s", metric.value, value, **kwargs)

    def gauge(self, metric: Metric, value, **kwargs):
        self._logger.info("Gauge '%s': %s", metric.value, value, **kwargs)

    def histogram(self, metric: Metric, value, **kwargs):
        self._logger.info("Histogram '%s': %s", metric.value, value, **kwargs)
