from typing import Protocol

from elena.domain.ports.strategy_manager import StrategyManager


class Strategy(Protocol):

    def init(self, strategy_manager: StrategyManager):
        ...

    def next(self):
        ...
