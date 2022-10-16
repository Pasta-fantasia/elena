from typing import Dict

from pydantic import BaseModel


class Order(BaseModel):
    bot_id: str
    strategy_id: str
    order: Dict  # TODO Transform to data
