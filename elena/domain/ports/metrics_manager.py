from enum import Enum
from typing import Protocol, runtime_checkable

import pandas as pd

from elena.domain.model.bot_config import BotConfig
from elena.domain.ports.logger import Logger
from elena.domain.ports.storage_manager import StorageManager


class Metric(str, Enum):
    ORDER_CANCELLED = "order_cancelled"


@runtime_checkable
class MetricsManager(Protocol):
    def init(self, config: dict, logger: Logger, storage_manager: StorageManager):
        ...

    def counter(self, metric: Metric, bot_config: BotConfig, value: int = 1):
        ...

    def gauge(self, metric: Metric, bot_config: BotConfig, value: float):
        ...

    def candles(self, bot_config: BotConfig, value: pd.DataFrame):
        ...
