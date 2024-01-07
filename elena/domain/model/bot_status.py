import time
from typing import List, Optional

from pydantic import BaseModel

from elena.domain.model.order import Order
from elena.domain.model.trade import Trade


class BotBudget(BaseModel):
    # Budget in quote to spend in the strategy.
    _free: float = 0
    _used: float = 0
    _budget_control: bool = False

    def set(self, budget: float):
        self._free = budget
        self._budget_control = (budget > 0)

    def lock(self, used: float):
        if self._budget_control and self._free > used:
            # raise?
            pass
        self._free = self._free - used
        self._used = self._used + used

    def unlock(self, released: float):
        if self._budget_control and self._used > released:
            # warning?
            pass
        self._free = self._free + released
        self._used = self._used - released

    @property
    def free(self):
        return self._free

    @property
    def used(self):
        return self._used

    @property
    def total(self):
        return self._free + self._used

    @property
    def is_budget_controlled(self):
        return self._budget_control


class BotStatus(BaseModel):
    bot_id: str
    timestamp: int = int(time.time() * 1000)
    active_orders: List[Order]
    archived_orders: List[Order]
    active_trades: List[Trade]
    closed_trades: List[Trade]
    budget: Optional[BotBudget] = None
