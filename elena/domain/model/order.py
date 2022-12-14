from typing import Optional, Dict, List

from pydantic import BaseModel
from pydantic.config import Enum

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


class TimeInForce(str, Enum):
    GTC = 'GTC'
    IOC = 'IOC'
    FOK = 'FOK'
    PO = 'PO'


class OrderSide(str, Enum):
    buy = 'buy'
    sell = 'sell'


class TakerOrMaker(str, Enum):
    taker = 'taker'
    maker = 'maker'


class Trade(BaseModel):
    id: str  # string trade id
    timestamp: int  # Unix timestamp in milliseconds
    taker_or_maker: TakerOrMaker
    price: float  # amount of base currency
    cost: float  # total cost, `price * amount`
    fee_currency: str  # which currency the fee is (usually quote)
    fee_cost: float  # the fee amount in that currency
    fee_rate: float  # the fee rate (if available)
    info: Dict  # the original decoded JSON as is


class Order(BaseModel):
    id: str
    bot_id: str
    strategy_id: str
    pair: TradingPair
    client_order_id: str  # a user-defined clientOrderId, if any
    timestamp: int  # order placing/opening Unix timestamp in milliseconds
    last_trade_timestamp: Optional[int]  # Unix timestamp of the most recent trade on this order
    status: OrderStatusType
    type: OrderType
    time_in_force: TimeInForce
    side: OrderSide
    price: float  # float price in quote currency (may be empty for market orders)
    average: float  # float average filling price
    amount: float  # ordered amount of base currency
    filled: float  # filled amount of base currency
    remaining: float  # remaining amount to fill
    cost: float  # 'filled' * 'price' (filling price used where available)
    trades: List[Trade]  # a list of order trades/executions
    fee_currency: str  # which currency the fee is (usually quote)
    fee_cost: float  # the fee amount in that currency
    fee_rate: float  # the fee rate (if available)
    info: Dict  # the original un-parsed order structure as is
