from typing import List, Protocol, runtime_checkable

from elena.domain.ports.logger import Logger
from elena.domain.ports.storage_manager import StorageManager

ORDER_CANCELLED = "OrderCancelled"
ORDER_STOP_LOSS = "OrderStopLoss"
ORDER_BUY_MARKET = "OrderBuyMarket"
ORDER_SELL_MARKET = "OrderSellMarket"
INDICATOR = "Indicator"


@runtime_checkable
class MetricsManager(Protocol):
    def init(self, config: dict, logger: Logger, storage_manager: StorageManager):
        ...

    def counter(self, metric: str, strategy_id: str, value: int, tags: List[str]):
        ...

    def gauge(self, metric: str, strategy_id: str, value: float, tags: List[str]):
        ...
