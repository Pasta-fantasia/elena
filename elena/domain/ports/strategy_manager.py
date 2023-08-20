import typing as t
from typing import Protocol

import pandas as pd

from elena.domain.model.order import Order
from elena.domain.model.order_book import OrderBook
from elena.domain.model.balance import Balance
from elena.domain.model.exchange import Exchange
from elena.domain.model.exchange import ExchangeType
from elena.domain.model.time_frame import TimeFrame
from elena.domain.model.trading_pair import TradingPair
from elena.domain.model.bot_config import BotConfig

class StrategyManager(Protocol):

    def get_exchange(self, exchange_id: ExchangeType) -> Exchange:
        ...

    def cancel_order(self, exchange: Exchange, bot_config: BotConfig, order_id: str) -> Order:
        ...

    # TODO: [Pere] I'm not sure if this is the place for this methods.
    def stop_loss_limit(self, exchange: Exchange, bot_config: BotConfig, amount: float, stop_price: float, price: float) -> Order:
        ...

    def get_balance(self, exchange: Exchange) -> Balance:
        ...

    def read_candles(self, exchange: Exchange, pair: TradingPair, time_frame: TimeFrame = TimeFrame.min_1) -> pd.DataFrame:
        ...

    def get_order_book(self) -> OrderBook:
        ...


