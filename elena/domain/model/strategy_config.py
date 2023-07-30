from typing import List

from pydantic import BaseModel

from elena.domain.model.bot_config import BotConfig


class StrategyConfig(BaseModel):
    id: str
    name: str
    enabled: bool = True
    strategy_class: str
    bots: List[BotConfig]
