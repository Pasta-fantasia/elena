import typing as t
from typing import Protocol

import pandas as pd

from elena.domain.model.balance import Balance
from elena.domain.model.bot_config import BotConfig
from elena.domain.model.exchange import Exchange, ExchangeType
from elena.domain.model.order import Order
from elena.domain.model.order_book import OrderBook
from elena.domain.model.time_frame import TimeFrame
from elena.domain.model.trading_pair import TradingPair


class StrategyManager(Protocol):
    def get_exchange(self, exchange_id: ExchangeType) -> t.Optional[Exchange]:
        ...

    def cancel_order(
        self, exchange: Exchange, bot_config: BotConfig, order_id: str
    ) -> Order:
        ...

    def stop_loss_limit(
        self,
        exchange: Exchange,
        bot_config: BotConfig,
        amount: float,
        stop_price: float,
        price: float,
    ) -> Order:
        ...

    def get_balance(self, exchange: Exchange) -> Balance:
        ...

    def read_candles(
        self,
        exchange: Exchange,
        pair: TradingPair,
        page_size: int,
        time_frame: TimeFrame = TimeFrame.min_1,  # type: ignore
    ) -> pd.DataFrame:
        ...

    def get_order_book(self) -> OrderBook:
        ...

    def limit_min_amount(self, exchange: Exchange, pair: TradingPair) -> float:
        ...

    def create_limit_buy_order(
        self, exchange: Exchange, bot_config: BotConfig, amount, price
    ) -> Order:
        ...

    def create_limit_sell_order(
        self, exchange: Exchange, bot_config: BotConfig, amount, price
    ) -> Order:
        ...

    def create_market_buy_order(
        self, exchange: Exchange, bot_config: BotConfig, amount
    ) -> Order:
        ...

    def create_market_sell_order(
        self, exchange: Exchange, bot_config: BotConfig, amount: float
    ) -> Order:
        ...

    def fetch_order(
        self, exchange: Exchange, pair: TradingPair, order_id: str
    ) -> Order:
        ...

    def amount_to_precision(
        self, exchange: Exchange, pair: TradingPair, amount: float
    ) -> float:
        ...

    def price_to_precision(
        self, exchange: Exchange, pair: TradingPair, price: float
    ) -> float:
        ...
