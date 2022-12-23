from typing import List

from pydantic import BaseModel


class PriceAmount(BaseModel):
    price: float
    amount: float


class OrderBook(BaseModel):
    bids: List[PriceAmount]
    asks: List[PriceAmount]
