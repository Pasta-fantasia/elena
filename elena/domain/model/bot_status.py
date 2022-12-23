import time
from typing import List

from pydantic import BaseModel

from elena.domain.model.order import Order


class BotStatus(BaseModel):
    bot_id: str
    timestamp: int = int(time.time() * 1000)
    orders: List[Order]
