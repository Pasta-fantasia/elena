from typing import Dict

from pydantic import BaseModel

from elena.domain.model.trading_pair import TradingPair


class BotConfig(BaseModel):
    bot_id: str
    name: str
    strategy_id: str
    enabled: bool = True
    pair: TradingPair
    config: Dict  # TODO Transform to data class
