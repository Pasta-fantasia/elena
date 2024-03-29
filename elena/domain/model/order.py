from typing import Optional

from pydantic import BaseModel
from pydantic.config import Enum

from elena.domain.model.exchange import ExchangeType
from elena.domain.model.trading_pair import TradingPair


class OrderStatusType(str, Enum):
    open = "open"
    closed = "closed"
    canceled = "canceled"
    expired = "expired"
    rejected = "rejected"


class OrderType(str, Enum):
    market = "market"
    limit = "limit"
    stop_loss_limit = "stop_loss_limit"


class OrderSide(str, Enum):
    buy = "buy"
    sell = "sell"


class Fee(BaseModel):
    currency: str  # which currency the fee is (usually quote)
    cost: float  # the fee amount in that currency
    rate: float  # the fee rate (if available)


class Order(BaseModel):
    id: str
    exchange_id: ExchangeType
    bot_id: str
    strategy_id: str
    pair: TradingPair
    timestamp: int  # order placing/opening Unix timestamp in milliseconds
    type: OrderType
    side: OrderSide
    price: float  # float price in quote currency (may be empty for market orders)
    amount: float  # ordered amount of base currency
    cost: Optional[float]  # 'filled' * 'price' (filling price used where available)
    average: Optional[float]  # float average filling price
    filled: Optional[float]  # filled amount of base currency
    remaining: Optional[float]  # remaining amount to fill
    status: Optional[OrderStatusType]
    fee: Optional[Fee]
    trigger_price: Optional[float]
    stop_price: Optional[float]
    take_profit_price: Optional[float]
    stop_loss_price: Optional[float]
    # parent_trade: Optional[str]
