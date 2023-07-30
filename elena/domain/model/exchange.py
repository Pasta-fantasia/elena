from pydantic import BaseModel
from pydantic.config import Enum


class ExchangeType(str, Enum):
    bitget = 'bitget'
    kucoin = 'kucoin'
    binance = 'binance'
    coinex = 'coinex'
    kraken = 'kraken'
    # TODO: can it be dynamic reading from cctx?


class Exchange(BaseModel):
    id: ExchangeType
    enabled: bool = True
    sandbox_mode: bool = False
    api_key: str
    password: str
    secret: str
    # TODO add commission... or can we get it from cctx?
    # TODO if id==ExchangeType => we can only have one account per exchange in a config file... is it ok?
