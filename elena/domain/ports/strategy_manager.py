import typing as t
from typing import Protocol

import pandas as pd

from elena.domain.model.order import Order
from elena.domain.model.order_book import OrderBook


class StrategyManager(Protocol):

    def buy(self):
        ...

    def sell(self):
        ...

    def stop_loss(self):
        ...

    def get_candles(self) -> pd.DataFrame:
        ...

    def get_order_book(self) -> OrderBook:
        ...

    def get_orders(self) -> t.List[Order]:
        ...
