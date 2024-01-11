# TODO: jsons should look like Binance_read_candles_BTC_USDT_min_1.
#  Record class was doing something like that. But the time parameter is not relevant anymore.
#       Not sure if that would be possible with amount_to_precision and price_to_precision
from test.elena.domain.services.record import Record
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
from elena.domain.ports.storage_manager import StorageManager

recording = False
excluded_kwargs = ["exchange"]
if recording:
    recorded_data = {}
else:
    recorded_data = Record.load_all_recorded_data()


class FakeExchangeManager(ExchangeManager):
    _cctx: CctxExchangeManager
    _logger: Logger

    def init(self, config: Dict, logger: Logger, storage_manager: StorageManager):
        self._cctx = CctxExchangeManager()
        self._cctx.init(config, logger, storage_manager)
        self._logger = logger

    @Record(enabled=recording, excluded_kwargs=excluded_kwargs)
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
            return Record.load_recorded_output(
                function_name="read_candles",
                all_recorded_data=recorded_data,
                pair=pair,
                time_frame=time_frame,
                page_size=page_size,
            )

    @Record(enabled=recording, excluded_kwargs=excluded_kwargs)
    def amount_to_precision(self, exchange: Exchange, pair: TradingPair, amount: float) -> float:
        if recording:
            return self._cctx.amount_to_precision(exchange, pair, amount)
        else:
            return Record.load_recorded_output(
                function_name="amount_to_precision",
                all_recorded_data=recorded_data,
                pair=pair,
                amount=amount,
            )

    @Record(enabled=recording, excluded_kwargs=excluded_kwargs)
    def price_to_precision(self, exchange: Exchange, pair: TradingPair, price: float) -> float:
        if recording:
            return self._cctx.price_to_precision(exchange, pair, price)
        else:
            return Record.load_recorded_output(
                function_name="price_to_precision",
                all_recorded_data=recorded_data,
                pair=pair,
                price=price,
            )

    @Record(enabled=recording, excluded_kwargs=excluded_kwargs)
    def read_order_book(self, exchange: Exchange, pair: TradingPair) -> OrderBook:
        if recording:
            result = self._cctx.read_order_book(exchange, pair)
            return result
        else:
            return Record.load_recorded_output(
                function_name="read_order_book",
                all_recorded_data=recorded_data,
                pair=pair,
            )

    @Record(enabled=recording, excluded_kwargs=excluded_kwargs)
    def get_balance(self, exchange: Exchange) -> Balance:
        if recording:
            return self._cctx.get_balance(exchange)
        else:
            return Record.load_recorded_output(
                function_name="get_balance",
                all_recorded_data=recorded_data,
            )

    @Record(enabled=recording, excluded_kwargs=excluded_kwargs)
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
            return self._cctx.place_order(exchange, bot_config, order_type, side, amount, price, params)
        else:
            return Record.load_recorded_output(
                function_name="place_order",
                all_recorded_data=recorded_data,
                bot_config=bot_config,
                order_type=order_type,
                side=side,
                amount=amount,
                price=price,
                params=params,
            )

    @Record(enabled=recording, excluded_kwargs=excluded_kwargs)
    def cancel_order(self, exchange: Exchange, bot_config: BotConfig, order_id: str):
        if recording:
            return self._cctx.cancel_order(exchange, bot_config, order_id)
        else:
            return Record.load_recorded_output(
                function_name="cancel_order",
                all_recorded_data=recorded_data,
                bot_config=bot_config,
                order_id=order_id,
            )

    @Record(enabled=recording, excluded_kwargs=excluded_kwargs)
    def fetch_order(self, exchange: Exchange, bot_config: BotConfig, order_id: str) -> Order:
        if recording:
            return self._cctx.fetch_order(exchange, bot_config, order_id)
        else:
            return Record.load_recorded_output(
                function_name="fetch_order",
                all_recorded_data=recorded_data,
                bot_config=bot_config,
                order_id=order_id,
            )

    @Record(enabled=recording, excluded_kwargs=excluded_kwargs)
    def limit_min_amount(self, exchange: Exchange, pair: TradingPair) -> float:
        if recording:
            return self._cctx.limit_min_amount(exchange, pair)
        else:
            return Record.load_recorded_output(
                function_name="limit_min_amount",
                all_recorded_data=recorded_data,
                pair=pair,
            )
