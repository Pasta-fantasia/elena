from typing import Optional, Dict, List

from pydantic import BaseModel
from pydantic.config import Enum

from elena.domain.model.exchange import ExchangeType
from elena.domain.model.trading_pair import TradingPair


class OrderStatusType(str, Enum):
    open = 'open'
    closed = 'closed'
    canceled = 'canceled'
    expired = 'expired'
    rejected = 'rejected'


class OrderType(str, Enum):
    market = 'market'
    limit = 'limit'


class OrderSide(str, Enum):
    buy = 'buy'
    sell = 'sell'


class TakerOrMaker(str, Enum):
    taker = 'taker'
    maker = 'maker'


class Fee(BaseModel):
    currency: str  # which currency the fee is (usually quote)
    cost: float  # the fee amount in that currency
    rate: float  # the fee rate (if available)


class Trade(BaseModel):
    id: str  # string trade id
    timestamp: int  # Unix timestamp in milliseconds
    taker_or_maker: TakerOrMaker
    price: float  # amount of base currency
    cost: float  # total cost, `price * amount`
    fee: Fee
    info: Dict  # the original decoded JSON as is


class Order(BaseModel):
    id: str
    exchange_id: ExchangeType
    bot_id: str
    strategy_id: str
    pair: TradingPair
    client_order_id: str  # a user-defined clientOrderId, if any
    timestamp: int  # order placing/opening Unix timestamp in milliseconds
    last_trade_timestamp: Optional[int]  # Unix timestamp of the most recent trade on this order
    type: OrderType
    side: OrderSide
    price: float  # float price in quote currency (may be empty for market orders)
    amount: float  # ordered amount of base currency
    cost: Optional[float]  # 'filled' * 'price' (filling price used where available)
    average: Optional[float]  # float average filling price
    filled: Optional[float]  # filled amount of base currency
    remaining: Optional[float]  # remaining amount to fill
    status: Optional[OrderStatusType]
    trades: List[Trade]  # a list of order trades/executions
    fee: Optional[Fee]
    info: Dict  # the original un-parsed order structure as is
