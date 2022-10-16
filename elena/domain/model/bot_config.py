from typing import Dict

from pydantic import BaseModel


class BotConfig(BaseModel):
    bot_id: str
    name: str
    strategy_id: str
    enabled: bool = True
    config: Dict  # TODO Transform to data class
