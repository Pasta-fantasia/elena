from typing import Protocol

from elena.domain.model.bot_config import BotConfig
from elena.domain.model.bot_status import BotStatus
from elena.domain.ports.strategy_manager import StrategyManager


class Strategy(Protocol):

    def init(self, manager: StrategyManager):
        ...

    def next(self, status: BotStatus, bot_config: BotConfig) -> BotStatus:
        ...
