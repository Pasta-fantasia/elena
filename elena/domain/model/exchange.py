from pydantic import BaseModel
from pydantic.config import Enum


class ExchangeType(str, Enum):
    bitget = 'bitget'
    kucoin = 'kucoin'
    binance = 'binance'


class Exchange(BaseModel):
    id: ExchangeType
    enabled: bool = True
    sandbox_mode: bool = False
    api_key: str
    password: str
    secret: str
