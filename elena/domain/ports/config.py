from typing import Protocol, List

from elena.domain.model.strategy_config import StrategyConfig


class Config(Protocol):
    def get(self, section_name: str, key: str, default_value=None):
        pass

    def get_strategies(self) -> List[StrategyConfig]:
        pass

    def home(self) -> str:
        pass
