from typing import Dict

from pydantic import BaseModel


class Summary(BaseModel):
    bot_id: str
    strategy_id: str
    summary: Dict  # TODO Transform to data class
