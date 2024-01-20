import time
from typing import List

from pydantic import BaseModel

from elena.domain.model.bot_budget import BotBudget
from elena.domain.model.order import Order
from elena.domain.model.trade import Trade


class BotStatus(BaseModel):
    bot_id: str
    timestamp: int = int(time.time() * 1000)
    budget: BotBudget
    active_orders: List[Order]
    archived_orders: List[Order]
    active_trades: List[Trade]
    closed_trades: List[Trade]
