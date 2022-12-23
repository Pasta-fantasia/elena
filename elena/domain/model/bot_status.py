import time
from typing import List

from pydantic import BaseModel

from elena.domain.model.bot_config import BotConfig
from elena.domain.model.order import Order


class BotStatus(BaseModel):
    timestamp: int = int(time.time() * 1000)
    config: BotConfig
    orders: List[Order]
