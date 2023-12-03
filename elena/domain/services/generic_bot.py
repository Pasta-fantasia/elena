from typing import Dict, Optional

import pandas as pd

from elena.domain.model.balance import Balance
from elena.domain.model.bot_config import BotConfig
from elena.domain.model.bot_status import BotStatus
from elena.domain.model.exchange import Exchange
from elena.domain.model.limits import Limits
from elena.domain.model.order import Order
from elena.domain.model.order_book import OrderBook
from elena.domain.model.time_frame import TimeFrame
from elena.domain.model.trading_pair import TradingPair
from elena.domain.ports.bot import Bot
from elena.domain.ports.logger import Logger
from elena.domain.ports.strategy_manager import StrategyManager


class GenericBot(Bot):
    id: str
    name: str
    pair: TradingPair
    exchange: Exchange
    time_frame: TimeFrame
    limits: Limits
    config: Dict
    manager: StrategyManager
    bot_config: BotConfig
    _logger: Logger

    def init(self, manager: StrategyManager, logger: Logger, bot_config: BotConfig):
        self.id = bot_config.id
        self.name = bot_config.name
        self.pair = bot_config.pair
        self.time_frame = bot_config.time_frame
        self.config = bot_config.config
        self.manager = manager
        self.bot_config = bot_config
        self._logger = logger

        exchange = manager.get_exchange(bot_config.exchange_id)
        if not exchange:
            raise Exception(f"Cannot get Exchange from {bot_config.exchange_id} ID")
        self.exchange = exchange  # type: ignore

    def next(self, status: BotStatus) -> Optional[BotStatus]:
        ...

    def cancel_order(self, order_id: str) -> Optional[Order]:
        try:
            return self.manager.cancel_order(
                self.exchange,
                self.bot_config,
                order_id,
            )
        except Exception as err:
            self._logger.error(f"Error cancelling order {order_id}: {err}", error=err)
            return None

    def get_balance(self) -> Optional[Balance]:
        try:
            return self.manager.get_balance(self.exchange)
        except Exception as err:
            self._logger.error(f"Error getting balance: {err}", error=err)
            return None

    def stop_loss(
        self, amount: float, stop_price: float, price: float
    ) -> Optional[Order]:
        try:
            return self.manager.stop_loss_limit(
                self.exchange,
                self.bot_config,
                amount,
                stop_price,
                price,
            )
        except Exception as err:
            self._logger.error(f"Error creating stop loss: {err}", error=err)
            return None

    def read_candles(
        self, page_size: int, time_frame: Optional[TimeFrame] = None
    ) -> pd.DataFrame:
        if not time_frame:
            time_frame = self.time_frame
        try:
            return self.manager.read_candles(
                self.exchange,
                self.pair,
                page_size,
                time_frame,
            )
        except Exception as err:
            self._logger.error(f"Error reading candles: {err}", error=err)
            return pd.DataFrame()

    def get_order_book(self) -> Optional[OrderBook]:
        try:
            return self.manager.get_order_book()
        except Exception as err:
            self._logger.error(f"Error getting order book: {err}", error=err)
            return None

    def limit_min_amount(self) -> Optional[float]:
        try:
            return self.manager.limit_min_amount(
                self.exchange,
                self.pair,
            )
        except Exception as err:
            self._logger.error(f"Error getting limit min amount: {err}", error=err)
            return None

    def create_limit_buy_order(self, amount, price) -> Optional[Order]:
        """buy (0.01 BTC at 47k USDT)  pair=BTC/UST"""
        try:
            return self.manager.create_limit_buy_order(
                self.exchange,
                self.bot_config,
                amount,
                price,
            )
        except Exception as err:
            self._logger.error(f"Error creating limit buy order: {err}", error=err)
            return None

    def create_limit_sell_order(self, amount, price) -> Optional[Order]:
        try:
            return self.manager.create_limit_sell_order(
                self.exchange,
                self.bot_config,
                amount,
                price,
            )
        except Exception as err:
            self._logger.error(f"Error creating limit sell order: {err}", error=err)
            return None

    def create_market_buy_order(self, amount) -> Optional[Order]:
        try:
            return self.manager.create_market_buy_order(
                self.exchange,
                self.bot_config,
                amount,
            )
        except Exception as err:
            self._logger.error(f"Error creating market buy order: {err}", error=err)
            return None

    def create_market_sell_order(self, amount) -> Optional[Order]:
        try:
            return self.manager.create_market_sell_order(
                self.exchange,
                self.bot_config,
                amount,
            )
        except Exception as err:
            self._logger.error(f"Error creating market sell order: {err}", error=err)
            return None

    def fetch_order(self, order_id: str) -> Optional[Order]:
        try:
            return self.manager.fetch_order(
                self.exchange,
                self.pair,
                order_id,
            )
        except Exception as err:
            self._logger.error(f"Error fetching order: {err}", error=err)
            return None
