import time
from typing import Optional

from pydantic import BaseModel

from elena.domain.model.exchange import ExchangeType
from elena.domain.model.trading_pair import TradingPair


class Trade(BaseModel):
    id: str = str(int(time.time() * 1000))  # all id are str
    exchange_id: ExchangeType
    bot_id: str
    strategy_id: str
    pair: TradingPair
    size: float  # ordered amount of base currency

    entry_time: int = 0  # order placing/opening Unix timestamp in milliseconds
    entry_price: float = 0.0
    entry_order_id: Optional[str] = "manual"
    entry_cost: float = 0.0

    exit_time: Optional[int] = 0  # order placing/opening Unix timestamp in milliseconds
    exit_price: Optional[float] = 0.0
    exit_order_id: Optional[str] = "manual"
    exit_cost: Optional[float] = 0.0

    duration: Optional[int] = 0
    return_pct: Optional[float] = 0.0
    profit: Optional[float] = 0.0
