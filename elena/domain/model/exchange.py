from pydantic import BaseModel
from pydantic.config import Enum


class ExchangeType(str, Enum):
    bitget = 'bitget'
    kucoin = 'kucoin'


class Exchange(BaseModel):
    id: ExchangeType
    enabled: bool = True
    api_key: str
    password: str
    secret: str
