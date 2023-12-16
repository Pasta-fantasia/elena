from enum import Enum
from typing import Protocol

from elena.domain.ports.logger import Logger


class Metric(str, Enum):
    ORDER_CANCELLED = "order_cancelled"


class MetricsManager(Protocol):
    def init(self, config: dict, logger: Logger):
        ...

    def counter(self, metric: Metric, value, **kwargs):
        ...

    def histogram(self, metric: Metric, value, **kwargs):
        ...
