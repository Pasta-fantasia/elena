from typing import Dict

from pydantic import BaseModel

from elena.domain.model.time_period import TimePeriod
from elena.domain.model.trading_pair import TradingPair


class MarketCandles(BaseModel):
    market_id: str
    trading_pair: TradingPair
    time_period: TimePeriod
    candles: Dict  # TODO Transform to data class
