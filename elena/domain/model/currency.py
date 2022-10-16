from pydantic.validators import Enum


class Currency(str, Enum):
    BTC = 'BTC'
    ETH = 'ETH'
    DOT = 'DOT'
    USDC = 'USDC'
    USDT = 'USDT'
