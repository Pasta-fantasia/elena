from pydantic import BaseModel

from elena.domain.model.currency import Currency


class TradingPair(BaseModel):
    base: Currency
    quote: Currency

    def __str__(self) -> str:
        return f'{self.base}/{self.quote}'
