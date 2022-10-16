from pydantic import BaseModel

from elena.domain.model.currency import Currency


class TradingPair(BaseModel):
    base: Currency
    quote: Currency

    @staticmethod
    def build(pair):
        _base, _quote = pair.split('/')
        return TradingPair(base=Currency(_base), quote=Currency(_quote))

    def __str__(self) -> str:
        return f'{self.base}/{self.quote}'
