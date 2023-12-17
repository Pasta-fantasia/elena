from typing import Optional, Protocol

from elena.domain.model.bot_config import BotConfig
from elena.domain.model.bot_status import BotStatus
from elena.domain.ports.exchange_manager import ExchangeManager
from elena.domain.ports.logger import Logger
from elena.domain.ports.metrics_manager import MetricsManager
from elena.domain.ports.strategy_manager import StrategyManager


class Bot(Protocol):
    """A Bot runs a strategy with a certain pair and configuration"""

    def init(
        self,
        manager: StrategyManager,
        logger: Logger,
        metrics_manager: MetricsManager,
        exchange_manager: ExchangeManager,
        bot_config: BotConfig,
        bot_status: BotStatus,
    ):
        ...

    def next(self) -> Optional[BotStatus]:
        ...
