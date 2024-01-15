from enum import Enum
from typing import List, Protocol, runtime_checkable

from elena.domain.ports.logger import Logger
from elena.domain.ports.storage_manager import StorageManager


class Metric(str, Enum):
    ORDER_CANCELLED = "OrderCancelled"
    INDICATOR = "Indicator"


@runtime_checkable
class MetricsManager(Protocol):
    def init(self, config: dict, logger: Logger, storage_manager: StorageManager):
        ...

    def counter(self, metric: Metric, strategy_id: str, value: int, tags: List[str]):
        ...

    def gauge(self, metric: Metric, strategy_id: str, value: float, tags: List[str]):
        ...
