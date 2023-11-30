from pydantic import BaseModel


class TradingPair(BaseModel):
    base: str
    quote: str

    @staticmethod
    def build(pair):
        base, _quote = pair.split("/")
        return TradingPair(base=base, quote=_quote)

    def __str__(self) -> str:
        return f"{self.base}/{self.quote}"
