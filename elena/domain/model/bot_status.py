from typing import Dict

from pydantic import BaseModel


class BotStatus(BaseModel):
    bot_id: str
    info: Dict
