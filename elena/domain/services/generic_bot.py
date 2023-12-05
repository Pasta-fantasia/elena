from typing import Dict, Optional

import pandas as pd

from elena.domain.model.balance import Balance
from elena.domain.model.bot_config import BotConfig
from elena.domain.model.bot_status import BotStatus
from elena.domain.model.exchange import Exchange
from elena.domain.model.limits import Limits
from elena.domain.model.order import Order, OrderSide, OrderStatusType, OrderType
from elena.domain.model.order_book import OrderBook
from elena.domain.model.time_frame import TimeFrame
from elena.domain.model.trading_pair import TradingPair
from elena.domain.ports.bot import Bot
from elena.domain.ports.exchange_manager import ExchangeManager
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
    exchange_manager: ExchangeManager
    bot_config: BotConfig
    initial_status: BotStatus  # for testing/development TODO: delete
    status: BotStatus
    _logger: Logger

    def _update_orders_status(self, exchange: Exchange, status: BotStatus, bot_config: BotConfig) -> BotStatus:
        # orders
        updated_orders = []
        for order in status.active_orders:
            # update status
            updated_order = self.fetch_order(order.id)

            if (updated_order.status == OrderStatusType.closed
                    or updated_order.status == OrderStatusType.canceled):
                # notify
                if updated_order.status == OrderStatusType.closed:
                    self._logger.info(
                        f"Notify! Order {updated_order.id} was closed for {updated_order.amount} {updated_order.pair} "
                        f"at {updated_order.average}"
                    )
                if updated_order.status == OrderStatusType.canceled:
                    self._logger.info(f"Notify! Order {updated_order.id} was cancelled!-")
                    # TODO: [Fran] what should we do if an order is cancelled? Cancel are: manual, something could go
                    #  wrong in L or the market is stopped.

                # updates trades
                for trade in status.active_trades:
                    if trade.exit_order_id == updated_order.id:
                        status.active_trades.remove(trade)
                        trade.exit_time = updated_order.timestamp
                        trade.exit_price = updated_order.average
                        status.closed_trades.append(trade)
                # move to archived
                status.archived_orders.append(updated_order)

            elif (updated_order.status == OrderStatusType.open
                  and updated_order and updated_order.filled > 0):  # type: ignore

                self._logger.info(f"Notify! Order {updated_order.id} is PARTIALLY_FILLED filled: "
                                  f"{updated_order.filled} of {updated_order.amount} {updated_order.pair} at"
                                  f" {updated_order.average}")

                # PARTIALLY_FILLED is considered an active order, It's on the strategy to do something.
                updated_orders.append(updated_order)
            else:
                updated_orders.append(updated_order)

        status.active_orders = updated_orders

        return status

    def init(self, manager: StrategyManager, logger: Logger, exchange_manager: ExchangeManager, bot_config: BotConfig,
             bot_status: BotStatus):
        self.id = bot_config.id
        self.name = bot_config.name
        self.pair = bot_config.pair
        self.time_frame = bot_config.time_frame
        self.config = bot_config.config
        self.manager = manager
        self.bot_config = bot_config
        self.initial_status = bot_status
        self._logger = logger

        exchange = manager.get_exchange(bot_config.exchange_id)
        if not exchange:
            raise Exception(f"Cannot get Exchange from {bot_config.exchange_id} ID")
        self.exchange = exchange  # type: ignore
        self.exchange_manager = exchange_manager
        self.status = self._update_orders_status(exchange, bot_status, bot_config)

    def next(self) -> Optional[BotStatus]:
        ...

    #  ---- Information

    def get_balance(self) -> Optional[Balance]:
        try:
            return self.exchange_manager.get_balance(self.exchange)
        except Exception:
            self._logger.error("Error creating stop loss", exc_info=1)
            return None

    def read_candles(
            self, time_frame: Optional[TimeFrame] = None, page_size: int = 100,
    ) -> pd.DataFrame:
        if not time_frame:
            time_frame = self.time_frame
        try:
            return self.exchange_manager.read_candles(
                self.exchange,
                self.pair,
                time_frame,
                page_size
            )
        except Exception:
            self._logger.error("Error reading candles", exc_info=1)
            return pd.DataFrame()

    def limit_min_amount(self) -> Optional[float]:
        try:
            return self.exchange_manager.limit_min_amount(
                self.exchange,
                self.pair,
            )
        except Exception:
            self._logger.error("Error getting limit min amount", exc_info=1)
            return None

    def amount_to_precision(self, amount: float) -> float:
        return self.exchange_manager.amount_to_precision(self.exchange, self.pair, amount)

    def price_to_precision(self, price: float) -> float:
        return self.exchange_manager.price_to_precision(self.exchange, self.pair, price)

    def get_order_book(self) -> Optional[OrderBook]:
        try:
            return self.exchange_manager.get_order_book()
        except Exception:
            self._logger.error("Error getting order book", exc_info=1)
            return None


    #  ---- Orders operations
    def cancel_order(self, order_id: str) -> Optional[Order]:
        try:
            return self.exchange_manager.cancel_order(self.exchange, self.bot_config, order_id)
        except Exception:
            self._logger.error(f"Error cancelling order {order_id}", exc_info=1)
            return None

    def stop_loss(self, amount: float, stop_price: float, price: float) -> Optional[Order]:
        try:
            amount = self.amount_to_precision(self.exchange, self.pair, amount)
            stop_price = self.price_to_precision(self.exchange, self.pair, stop_price)
            price = self.price_to_precision(self.exchange, self.pair, price)

            params = {"type": "spot", "triggerPrice": stop_price, "timeInForce": "GTC"}

            order = self.exchange_manager.place_order(
                exchange=self.exchange,
                bot_config=self.bot_config,
                order_type=OrderType.limit,  # type: ignore
                side=OrderSide.sell,  # type: ignore
                amount=amount,
                price=price,
                params=params,
            )
            self._logger.info("Placed market stop loss: %s", order)
            self.status.active_orders.append(order)
            return order
        except Exception:
            self._logger.error(f"Error creating stop loss.", exc_info=1)
            return None

    def create_limit_buy_order(self, amount, price) -> Optional[Order]:
        """buy (0.01 BTC at 47k USDT)  pair=BTC/UST"""
        raise NotImplementedError

    def create_limit_sell_order(self, amount, price) -> Optional[Order]:
        raise NotImplementedError

    def create_market_buy_order(self, amount) -> Optional[Order]:
        try:
            params = {"type": "spot"}

            amount = self.amount_to_precision(amount)
            order = self.exchange_manager.place_order(
                exchange=self.exchange,
                bot_config=self.bot_config,
                order_type=OrderType.market,  # type: ignore
                side=OrderSide.buy,  # type: ignore
                amount=amount,
                params=params,
            )
            self._logger.info("Placed market buy: %s", order)
            # TODO: order_add + trade_start (going long) | trade_stop (going short)
            self.status.active_orders.append(order)
            return order
        except Exception:
            self._logger.error(f"Error creating market buy order", exc_info=1)
            return None

    def create_market_sell_order(self, amount) -> Optional[Order]:
        try:
            params = {"type": "spot"}

            amount = self.amount_to_precision(amount)
            order = self.exchange_manager.place_order(
                exchange=self.exchange,
                bot_config=self.bot_config,
                order_type=OrderType.market,  # type: ignore
                side=OrderSide.sell,  # type: ignore
                amount=amount,
                params=params,
            )
            self._logger.info("Placed market sell: %s", order)
            # TODO: order_add + trade_stop (going long) | trade_start (going short)
            self.status.active_orders.append(order)
            return order
        except Exception:
            self._logger.error(f"Error creating market sell order ", exc_info=1)
            return None

    def fetch_order(self, order_id: str) -> Optional[Order]:
        try:
            return self.exchange_manager.fetch_order(
                self.exchange,
                self.bot_config,
                order_id,
            )
        except Exception:
            self._logger.error(f"Error fetching order",  exc_info=1)
            return None
