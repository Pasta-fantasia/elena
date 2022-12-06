from typing import Dict, List

from pydantic import BaseModel

from elena.domain.model.trading_pair import TradingPair


class BotConfig(BaseModel):
    id: str
    strategy_id: str
    name: str
    enabled: bool = True
    pair: TradingPair
    exchange_id: str
    tags: List[str]
    config: Dict  # TODO Transform to data class
