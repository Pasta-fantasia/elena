import json
from os.path import dirname, join, realpath
# TODO: jsons should look like Binance_read_candles_BTC_USDT_min_1.
#  Record class was doing something like that. But the time parameter is not relevant anymore.
#       Not sure if that would be possible with amount_to_precision and price_to_precision
from typing import Dict, Optional

import pandas as pd

from elena.adapters.exchange_manager.cctx_exchange_manager import \
    CctxExchangeManager
from elena.domain.model.balance import Balance
from elena.domain.model.bot_config import BotConfig
from elena.domain.model.exchange import Exchange
from elena.domain.model.order import Order, OrderSide, OrderType
from elena.domain.model.order_book import OrderBook
from elena.domain.model.time_frame import TimeFrame
from elena.domain.model.trading_pair import TradingPair
from elena.domain.ports.exchange_manager import ExchangeManager
from elena.domain.ports.logger import Logger
from test.elena.domain.services.record import Record

recording = True
excluded = ["Exchange", "FakeExchangeManager"]


class FakeExchangeManager(ExchangeManager):
    def __init__(self, config: Dict, logger: Logger):
        self._cctx = CctxExchangeManager(config, logger)
        self._logger = logger

    @Record(enabled=recording, excluded_args=excluded)
    def read_candles(
        self,
        exchange: Exchange,
        pair: TradingPair,
        time_frame: TimeFrame = TimeFrame.min_1,  # type: ignore
        page_size: int = 100,
    ) -> pd.DataFrame:
        if recording:
            return self._cctx.read_candles(exchange, pair, time_frame, page_size)
        else:
            return Record.deserialize_from_json("231208-1702060797568-read_candles.json")

    @Record(enabled=recording, excluded_args=excluded)
    def amount_to_precision(
        self, exchange: Exchange, pair: TradingPair, amount: float
    ) -> float:
        if recording:
            result = self._cctx.amount_to_precision(exchange, pair, amount)
            return result
        else:
            return Record.deserialize_from_json("231208-1702060471629-amount_to_precision.json")

    @Record(enabled=recording, excluded_args=excluded)
    def price_to_precision(
        self, exchange: Exchange, pair: TradingPair, price: float
    ) -> float:
        if recording:
            result = self._cctx.price_to_precision(exchange, pair, price)
            return result
        else:
            return Record.deserialize_from_json("231208-1702060548188-price_to_precision.json")

    @Record(enabled=recording, excluded_args=excluded)
    def read_order_book(self, exchange: Exchange, pair: TradingPair) -> OrderBook:
        if recording:
            result = self._cctx.read_order_book(exchange, pair)
            return result
        else:
            return Record.deserialize_from_json("231208-1702060668178-read_order_book.json")

    @Record(enabled=recording, excluded_args=excluded)
    def get_balance(self, exchange: Exchange) -> Balance:
        if recording:
            result = self._cctx.get_balance(exchange)
            return result
        else:
            return Record.deserialize_from_json("231208-1702061654266-get_balance.json")

    @Record(enabled=recording, excluded_args=excluded)
    def place_order(
        self,
        exchange: Exchange,
        bot_config: BotConfig,
        order_type: OrderType,
        side: OrderSide,
        amount: float,
        price: Optional[float] = None,
        params: Optional[Dict] = {},
    ) -> Order:
        if recording:
            return self._cctx.place_order(
                exchange, bot_config, order_type, side, amount, price, params
            )
        else:
            return Record.deserialize_from_json("231208-1702061654266-place_order.json")

    @Record(enabled=recording, excluded_args=excluded)
    def cancel_order(self, exchange: Exchange, bot_config: BotConfig, order_id: str):
        if recording:
            return self._cctx.cancel_order(exchange, bot_config, order_id)
        else:
            return Record.deserialize_from_json("231208-1702061654266-cancel_order.json")

    @Record(enabled=recording, excluded_args=excluded)
    def fetch_order(
        self, exchange: Exchange, bot_config: BotConfig, order_id: str
    ) -> Order:
        if recording:
            return self._cctx.fetch_order(exchange, bot_config, order_id)
        else:
            return Record.deserialize_from_json("231208-1702061654266-fetch_order.json")

    @Record(enabled=recording, excluded_args=excluded)
    def limit_min_amount(self, exchange: Exchange, pair: TradingPair) -> float:
        if recording:
            return self._cctx.limit_min_amount(exchange, pair)
        else:
            return Record.deserialize_from_json("231208-1702061654266-limit_min_amount.json")
