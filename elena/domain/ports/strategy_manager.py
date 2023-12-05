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

