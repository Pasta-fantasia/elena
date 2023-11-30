from typing import Protocol

from elena.domain.model.bot_config import BotConfig
from elena.domain.model.bot_status import BotStatus
from elena.domain.ports.logger import Logger
from elena.domain.ports.strategy_manager import StrategyManager


class Bot(Protocol):
    """ A Bot runs a strategy with a certain pair and configuration"""

    def init(self, manager: StrategyManager, logger: Logger, bot_config: BotConfig):
        ...

    def next(self, status: BotStatus) -> BotStatus:
        ...
