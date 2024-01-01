import logging
from typing import Dict, Optional

import pandas as pd

from elena.domain.model.balance import Balance
from elena.domain.model.bot_config import BotConfig
from elena.domain.model.bot_status import BotStatus
from elena.domain.model.exchange import Exchange
from elena.domain.model.limits import Limits
from elena.domain.model.order import (Order, OrderSide, OrderStatusType,
                                      OrderType)
from elena.domain.model.order_book import OrderBook
from elena.domain.model.time_frame import TimeFrame
from elena.domain.model.trade import Trade
from elena.domain.model.trading_pair import TradingPair
from elena.domain.ports.bot import Bot
from elena.domain.ports.exchange_manager import ExchangeManager
from elena.domain.ports.logger import Logger
from elena.domain.ports.metrics_manager import Metric, MetricsManager
from elena.domain.ports.notifications_manager import NotificationsManager
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
    _metrics_manager: MetricsManager
    _notifications_manager: NotificationsManager

    def init(
        self,
        manager: StrategyManager,
        logger: Logger,
        metrics_manager: MetricsManager,
        notifications_manager: NotificationsManager,
        exchange_manager: ExchangeManager,
        bot_config: BotConfig,
        bot_status: BotStatus,
    ):
        self.bot_config = bot_config
        self.id = bot_config.id
        self.name = bot_config.name
        self.pair = bot_config.pair
        self.time_frame = bot_config.time_frame
        self.config = bot_config.config
        self.manager = manager
        self.bot_config = bot_config
        self.initial_status = bot_status  # for testing/development TODO: delete
        self.status = bot_status
        self._logger = logger
        self._metrics_manager = metrics_manager
        self._notifications_manager = notifications_manager

        exchange = manager.get_exchange(bot_config.exchange_id)
        if not exchange:
            raise Exception(f"Cannot get Exchange from {bot_config.exchange_id} ID")
        self.exchange = exchange  # type: ignore
        self.exchange_manager = exchange_manager
        self._update_orders_status()

    #  ---- StatusManager

    def new_trade_by_order(self, order: Order):
        # All Trades start/"born" here...
        new_trade = Trade(
            exchange_id=self.exchange.id,
            bot_id=self.id,
            strategy_id=self.bot_config.strategy_id,
            pair=self.pair,
            size=order.amount,
            entry_order_id=order.id,
            entry_price=order.average,
            entry_time=order.timestamp,
            exit_order_id=0,
            exit_price=0,
        )
        self.status.active_trades.append(new_trade)

    def new_trade_manual(self, size: float, entry_price: float, exit_order_id, exit_price: float):
        new_trade = Trade(
            exchange_id=self.exchange.id,
            bot_id=self.id,
            strategy_id=self.bot_config.strategy_id,
            pair=self.pair,
            size=size,
            entry_order_id="manual",
            entry_price=entry_price,
            exit_order_id=exit_order_id,
            exit_price=exit_price,
        )
        self.status.active_trades.append(new_trade)

    def _close_individual_trade_on_new_order(self, trade: Trade, order: Order, amount_to_close: float) -> float:
        if trade.size <= amount_to_close:
            self.status.active_trades.remove(trade)
            trade.exit_time = order.timestamp
            trade.exit_price = order.average
            self.status.closed_trades.append(trade)
        else:
            self._logger.error(f"Amount to close is insufficient for id:{trade.id} size: {trade.size}")
        return amount_to_close - trade.size

    def close_trades_on_new_order(self, order: Order):
        amount_to_close = order.amount
        # check trades with an exit order id
        for trade in self.status.active_trades:
            if trade.exit_order_id == order.id and amount_to_close > 0:
                amount_to_close = self._close_individual_trade_on_new_order(trade, order, amount_to_close)

        # check trades without an exit order id
        if amount_to_close > 0:
            for trade in self.status.active_trades:
                if trade.exit_order_id == 0 and amount_to_close > 0:
                    amount_to_close = self._close_individual_trade_on_new_order(trade, order, amount_to_close)

        # close trade even with a different order_id
        if amount_to_close > 0:
            self._logger.warning("The order size is bigger than the trades with an explicit order_id or a blank order_id")
            for trade in self.status.active_trades:
                if amount_to_close > 0:
                    amount_to_close = self._close_individual_trade_on_new_order(trade, order, amount_to_close)

        if amount_to_close > 0:
            self._logger.error("The order size is bigger than any trade")

    def _register_new_order_on_trades(self, order: Order):
        if order is None:
            raise "Order can't be None"

        # TODO OrderStatusType.canceled or rejected
        if order.status == OrderStatusType.canceled or order.status == OrderStatusType.rejected:
            raise "Order condition unhandled (canceled or rejected)"

        if order.side == OrderSide.buy:
            self.new_trade_by_order(order)
            # TODO: budget.lock
            if order.status == OrderStatusType.closed:
                self.status.archived_orders.append(order)
            else:  # open & partials are active, budget is lock equally.
                self.status.active_orders.append(order)

        elif order.side == OrderSide.sell:
            if order.status == OrderStatusType.closed:
                # TODO: budget.unlock
                self.close_trades_on_new_order(order)
                self.status.archived_orders.append(order)
            else:
                # stop loss => if order.stop_price and order.stop_price > 0:
                # TODO: budget.unlock (partial) ???
                self.status.active_orders.append(order)
        else:
            raise "Order condition unhandled (OrderSide)"

    def _archive_order_close_trades_on_update_orders(self, order: Order):
        for trade in self.status.active_trades:
            if trade.exit_order_id == order.id:
                self.status.active_trades.remove(trade)
                trade.exit_time = order.timestamp
                trade.exit_price = order.average
                self.status.closed_trades.append(trade)
        # move to archived
        self.status.archived_orders.append(order)

    def _archive_order_on_cancel(self, order: Order):
        for loop_order in self.status.active_orders:
            if loop_order.id == order.id:
                self.status.active_orders.remove(loop_order)
        self.status.archived_orders.append(order)

    def _update_orders_status(self) -> BotStatus:
        # orders
        updated_orders = []
        for order in self.status.active_orders:
            # update status
            updated_order = self.fetch_order(order.id)

            if updated_order:
                if updated_order.status == OrderStatusType.closed or updated_order.status == OrderStatusType.canceled:
                    # notify
                    if updated_order.status == OrderStatusType.closed:
                        self._logger.info(f"Notify! Order {updated_order.id} " f"was closed for {updated_order.amount} {updated_order.pair} " f"at {updated_order.average}")
                    if updated_order.status == OrderStatusType.canceled:
                        self._logger.info(f"Notify! Order {updated_order.id} was cancelled!-")
                        # TODO: [Fran] what should we do if an order is cancelled?
                        #  Cancel are: manual, something could go
                        #  wrong in L or the market is stopped.

                    # updates trades
                    self._archive_order_close_trades_on_update_orders(updated_order)

                elif updated_order.status == OrderStatusType.open and updated_order.filled > 0:  # type: ignore

                    self._logger.info(f"Notify! Order {updated_order.id} is PARTIALLY_FILLED filled: " f"{updated_order.filled} of {updated_order.amount} {updated_order.pair} at" f" {updated_order.average}")

                    # PARTIALLY_FILLED is considered an active order, It's on the strategy to do something.
                    updated_orders.append(updated_order)
                else:
                    updated_orders.append(updated_order)
            else:
                self._logger.error(f"The order {order.id} has desapear! This should only happend on test environments")

        self.status.active_orders = updated_orders
        return self.status

    #  ---- Main

    def next(self) -> Optional[BotStatus]:
        ...

    #  ---- Information

    def get_balance(self) -> Optional[Balance]:
        try:
            return self.exchange_manager.get_balance(self.exchange)
        except Exception as err:
            print(f"Error getting balance: {err}")
            self._logger.error("Error creating stop loss", exc_info=1)
            return None

    def read_candles(
        self,
        time_frame: Optional[TimeFrame] = None,
        page_size: int = 100,
    ) -> pd.DataFrame:
        if not time_frame:
            time_frame = self.time_frame
        try:
            return self.exchange_manager.read_candles(
                self.exchange,
                pair=self.pair,
                time_frame=time_frame,
                page_size=page_size,
            )
        except Exception as err:
            print(f"Error reading candles: {err}")
            self._logger.error("Error reading candles", exc_info=1)
            return pd.DataFrame()

    def limit_min_amount(self) -> Optional[float]:
        try:
            return self.exchange_manager.limit_min_amount(
                self.exchange,
                pair=self.pair,
            )
        except Exception as err:
            print(f"Error getting limit min amount: {err}")
            self._logger.error("Error getting limit min amount", exc_info=1)
            return None

    def amount_to_precision(self, amount: float) -> Optional[float]:
        try:
            return self.exchange_manager.amount_to_precision(
                self.exchange,
                pair=self.pair,
                amount=amount,
            )
        except Exception as err:
            print(f"Error getting amount to precision: {err}")
            self._logger.error("Error getting amount to precision", exc_info=1)
            return None

    def price_to_precision(self, price: float) -> Optional[float]:
        try:
            return self.exchange_manager.price_to_precision(
                self.exchange,
                pair=self.pair,
                price=price,
            )
        except Exception as err:
            print(f"Error getting price to precision: {err}")
            self._logger.error("Error getting price to precision", exc_info=1)
            return None

    def get_order_book(self) -> Optional[OrderBook]:
        try:
            return self.exchange_manager.read_order_book(
                self.exchange,
                pair=self.pair,
            )
        except Exception as err:
            print(f"Error getting order book: {err}")
            self._logger.error("Error getting order book", exc_info=1)
            return None

    #  ---- Orders operations
    def cancel_order(self, order_id: str) -> Optional[Order]:
        try:
            order = self.exchange_manager.cancel_order(
                self.exchange,
                bot_config=self.bot_config,
                order_id=order_id,
            )
            self._metrics_manager.counter(Metric.ORDER_CANCELLED, self.bot_config)
            self._notifications_manager.medium(f"Order {order_id} was cancelled")
            self._archive_order_on_cancel(order)
            return order
        except Exception as err:
            print(f"Error cancelling order: {err}")
            self._logger.error(f"Error cancelling order {order_id}", exc_info=1)
            return None

    def stop_loss(self, amount: float, stop_price: float, price: float) -> Optional[Order]:
        # TODO: https://dev.binance.vision/t/code-1013-msg-filter-failure-percent-price/1592 PERCENT_PRICE filter
        #   while testing we got "'binance {"code":-1013,"msg":"Filter failure: PERCENT_PRICE_BY_SIDE"}'"
        try:
            precision_amount = self.amount_to_precision(amount)
            if not precision_amount:
                raise Exception(f"Cannot get amount to precision for {amount}")
            precision_stop_price = self.price_to_precision(stop_price)
            if not precision_stop_price:
                raise Exception(f"Cannot get stop_price to precision for {stop_price}")
            precision_price = self.price_to_precision(price)
            if not precision_price:
                raise Exception(f"Cannot get price to precision for {price}")

            params = {
                "type": "spot",
                "triggerPrice": precision_stop_price,
                "timeInForce": "GTC",
            }

            order = self.exchange_manager.place_order(
                self.exchange,
                bot_config=self.bot_config,
                order_type=OrderType.limit,  # type: ignore
                side=OrderSide.sell,  # type: ignore
                amount=precision_amount,
                price=precision_price,
                params=params,
            )
            self._logger.info("Placed market stop loss: %s", order)

            self._register_new_order_on_trades(order)
            return order
        except Exception as err:
            print(f"Error creating stop loss: {err}")
            self._logger.error("Error creating stop loss.", exc_info=1)
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
                self.exchange,
                bot_config=self.bot_config,
                order_type=OrderType.market,  # type: ignore
                side=OrderSide.buy,  # type: ignore
                amount=amount,
                params=params,
            )
            self._logger.info("Placed market buy: %s", order)

            self._register_new_order_on_trades(order)
            return order
        except Exception as err:
            print(f"Error creating market buy order: {err}")
            self._logger.error("Error creating market buy order", exc_info=1)
            return None

    def create_market_sell_order(self, amount) -> Optional[Order]:
        try:
            params = {"type": "spot"}

            amount = self.amount_to_precision(amount)
            order = self.exchange_manager.place_order(
                self.exchange,
                bot_config=self.bot_config,
                order_type=OrderType.market,  # type: ignore
                side=OrderSide.sell,  # type: ignore
                amount=amount,
                params=params,
            )
            self._logger.info("Placed market sell: %s", order)

            self._register_new_order_on_trades(order)
            return order
        except Exception as err:
            print(f"Error creating market sell order: {err}")
            self._logger.error("Error creating market sell order ", exc_info=1)
            return None

    def fetch_order(self, order_id: str) -> Optional[Order]:
        try:
            return self.exchange_manager.fetch_order(
                self.exchange,
                bot_config=self.bot_config,
                order_id=order_id,
            )
        except Exception as err:
            print(f"Error fetching order: {err}")
            self._logger.error("Error fetching order", exc_info=1)
            return None

    def get_estimated_last_close(self) -> float:
        # https://docs.ccxt.com/#/?id=ticker-structure
        # Although some exchanges do mix-in orderbook's top bid/ask prices into their tickers
        # (and some exchanges even serve top bid/ask volumes) you should not treat a ticker as a fetchOrderBook
        # replacement. The main purpose of a ticker is to serve statistical data, as such,
        # treat it as "live 24h OHLCV". It is known that exchanges discourage frequent fetchTicker requests by
        # imposing stricter rate limits on these queries. If you need a unified way to access bids and asks you
        # should use fetchL[123]OrderBook family instead.
        # The idea was to use fetch_ticker[close]
        try:
            order_book = self.exchange_manager.read_order_book(
                self.exchange,
                pair=self.pair,
            )
            last_bid = order_book.bids[0].price
            last_ask = order_book.asks[0].price
            estimated_last_close = (last_bid + last_ask) / 2
            return estimated_last_close
        except Exception as err:
            print(f"Error getting estimated last close: {err}")
            self._logger.error("Error fetching order", exc_info=1)
            raise err
