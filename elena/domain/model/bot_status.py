from typing import Dict

from pydantic import BaseModel


class BotStatus(BaseModel):
    bot_id: str
    timestamp: float
    status: Dict  # TODO Transform to data class
