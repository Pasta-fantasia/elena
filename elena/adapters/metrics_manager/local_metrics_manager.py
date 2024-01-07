import time
from typing import List, Union

import pandas as pd

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

    def counter(self, metric: Metric, strategy_id: str, value: int, tags: List[str]):
        self._save_metric("Counter", metric, strategy_id, value, tags)

    def gauge(self, metric: Metric, strategy_id: str, value: float, tags: List[str]):
        self._save_metric("Gauge", metric, strategy_id, value, tags)

    def _save_metric(self, metric_type: str, metric: Metric, strategy_id: str, value: Union[int, float], tags: List[str]):
        data = {
            "time": self._get_time(),
            "value": value,
            "tags": ", ".join(tags),
        }
        df = pd.DataFrame(data=data, index=[0])

        df_id = self._get_dataframe_id(metric_type, metric, strategy_id)
        self._storage_manager.save_data_frame(df_id, df)
        self._logger.info("%s %s %s: %s", metric_type, metric.value, strategy_id, value)

    @staticmethod
    def _get_dataframe_id(metric_type: str, metric: Metric, strategy_id: str) -> str:
        return f"{metric_type}-{metric.value}-{strategy_id}"

    @staticmethod
    def _get_time():
        return int(time.time() * 1000)
