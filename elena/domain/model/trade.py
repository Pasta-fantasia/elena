from typing import Optional

from pydantic import BaseModel
from pydantic.config import Enum

from elena.domain.model.exchange import ExchangeType
from elena.domain.model.trading_pair import TradingPair
from elena.domain.model.order import Order


class Trade(BaseModel):
    id: str
    exchange_id: ExchangeType
    bot_id: str
    strategy_id: str
    pair: TradingPair
    size: float  # ordered amount of base currency

    entry_time: int  # order placing/opening Unix timestamp in milliseconds
    entry_price: float
    entry_order: Order

    exit_time: int  # order placing/opening Unix timestamp in milliseconds
    exit_price: float
    exit_order: Order

    duration: int
    return_pct: float
