from pydantic import BaseModel
from pydantic.config import Enum


class ExchangeType(str, Enum):
    bitget = 'bitget'
    kucoin = 'kucoin'
    binance = 'binance'
    coinex = 'coinex'
    kraken = 'kraken'
    # TODO: [Pere] can it be dynamic reading from cctx? If we have to add each exchange by code we must release a new version.


class Exchange(BaseModel):
    id: ExchangeType
    enabled: bool = True
    sandbox_mode: bool = False
    api_key: str
    password: str
    secret: str
    # TODO: [Pere] add commission... or can we get it from cctx?...
    # TODO: [Pere] new_order_size <- round to asset precision Read: https://docs.ccxt.com/#/README?id=currency-structure
    #       market = exchange.market(symbol)
    #       and check if it fits the minimum tradable
    #       we also need access other limits like market['info']['filters'] #['filterType']['MAX_NUM_ALGO_ORDERS']
    #       I'm not saying this is the place to put it...
    # TODO: [Pere] High priority
    # TODO [Pere] if id==ExchangeType => we can only have one account per exchange in a config file... is it ok? OK for now!
