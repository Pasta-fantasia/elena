from typing import Dict, List

from pydantic import BaseModel

from elena.domain.model.exchange import ExchangeType
from elena.domain.model.time_frame import TimeFrame
from elena.domain.model.trading_pair import TradingPair


class BotConfig(BaseModel):
    id: str
    strategy_id: str
    name: str
    enabled: bool = True
    pair: TradingPair
    exchange_id: ExchangeType
    time_frame: TimeFrame
    cron_expression: str
    budget_limit: float = 0.0
    pct_reinvest_profit: float = 100.0
    tags: List[str]
    config: Dict
