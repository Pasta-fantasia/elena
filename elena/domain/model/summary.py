from typing import Dict, List

from pydantic import BaseModel

from elena.domain.model.order import Order


class Summary(BaseModel):
    bot_id: str
    strategy_id: str
    orders: List[Order]
    info: Dict
