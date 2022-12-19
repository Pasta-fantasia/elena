from pydantic.validators import Enum


class Currency(str, Enum):
    BNB = 'BNB'
    BTC = 'BTC'
    BUSD = 'BUSD'
    DOT = 'DOT'
    ETH = 'ETH'
    EUR = 'EUR'
    KCS = 'KCS'
    USD = 'USD'
    USDC = 'USDC'
    USDT = 'USDT'
