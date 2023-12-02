import json
from os.path import dirname, join, realpath
from typing import Dict, Optional

import pandas as pd

from elena.adapters.exchange_manager.cctx_exchange_manager import CctxExchangeManager
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

class FakeExchangeManager(ExchangeManager):
    def __init__(self, config: Dict, logger: Logger):
        self._cctx = CctxExchangeManager(config, logger)
        self._logger = logger

    @staticmethod
    def _load_from_json(filename: str) -> Dict:
        _filename = join(dirname(realpath(__file__)), "data", f"{filename}.json")
        with open(_filename, "r") as f:
            return json.load(f)

    @staticmethod
    def save_to_json(cache: Dict, filename: str):
        _filename = join(dirname(realpath(__file__)), "data", f"{filename}.json")
        with open(_filename, "w") as f:
            json.dump(cache, f)

    def read_candles(
        self,
        exchange: Exchange,
        pair: TradingPair,
        time_frame: TimeFrame = TimeFrame.min_1,  # type: ignore
    ) -> pd.DataFrame:
        data = self._load_from_json("read_candles")
        result = pd.DataFrame.from_dict(data)
        return result

    def amount_to_precision(
        self, exchange: Exchange, pair: TradingPair, amount: float
    ) -> float:
        result = self._cctx.amount_to_precision(exchange, pair, amount)
        return result

    def price_to_precision(
        self, exchange: Exchange, pair: TradingPair, price: float
    ) -> float:
        result = self._cctx.price_to_precision(exchange, pair, price)
        return result

    def read_order_book(self, exchange: Exchange, pair: TradingPair) -> OrderBook:
        result = self._cctx.read_order_book(exchange, pair)
        self.save_to_json(result.dict(), "read_order_book")
        return result

    def get_balance(self, exchange: Exchange) -> Balance:
        data = self._load_from_json("get_balance")
        result = Balance.parse_obj(data)
        return result

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
        result = self._cctx.place_order(
            exchange, bot_config, order_type, side, amount, price, params
        )
        self.save_to_json(result.dict(), "place_order")
        return result

    def cancel_order(self, exchange: Exchange, bot_config: BotConfig, order_id: str):
        result = self._cctx.cancel_order(exchange, bot_config, order_id)
        self.save_to_json(result.dict(), "cancel_order")
        return result

    def fetch_order(
        self, exchange: Exchange, bot_config: BotConfig, order_id: str
    ) -> Order:
        result = self._cctx.fetch_order(exchange, bot_config, order_id)
        self.save_to_json(result.dict(), "fetch_order")
        return result

    def limit_min_amount(self, exchange: Exchange, pair: TradingPair) -> float:
        return 1e-05
