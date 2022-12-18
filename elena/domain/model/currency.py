from pydantic.validators import Enum


class Currency(str, Enum):
    BTC = 'BTC'
    BUSD = 'BUSD'
    DOT = 'DOT'
    ETH = 'ETH'
    EUR = 'EUR'
    USD = 'USD'
    USDC = 'USDC'
    USDT = 'USDT'
