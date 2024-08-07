import time
from typing import Dict, Optional, List

import pandas as pd

from elena.domain.model.balance import Balance
from elena.domain.model.bot_config import BotConfig
from elena.domain.model.bot_status import BotStatus
from elena.domain.model.exchange import Exchange
from elena.domain.model.limits import Limits
from elena.domain.model.order import Order, OrderSide, OrderStatusType, OrderType
from elena.domain.model.order_book import OrderBook
from elena.domain.model.time_frame import TimeFrame
from elena.domain.model.trade import Trade
from elena.domain.model.trading_pair import TradingPair
from elena.domain.ports.bot import Bot
from elena.domain.ports.exchange_manager import ExchangeManager
from elena.domain.ports.logger import Logger
from elena.domain.ports.metrics_manager import MetricsManager, ORDER_CANCELLED, ORDER_STOP_LOSS, ORDER_BUY_MARKET, ORDER_SELL_MARKET, ORDER_STOP_LOSS_CLOSED, ESTIMATED_LAST_CLOSE, ESTIMATED_SALE_PRICE
from elena.domain.ports.notifications_manager import NotificationsManager
from elena.domain.ports.strategy_manager import StrategyManager
from elena.domain.services.bot_status_logic import BotStatusLogic


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
    status: BotStatus
    _logger: Logger
    _metrics_manager: MetricsManager
    _notifications_manager: NotificationsManager
    _bot_status_logic: BotStatusLogic
    _order_book_cache: OrderBook

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
        self.status = bot_status
        self.status.budget.set(bot_config.budget_limit)
        self.status.budget.pct_reinvest_profit = bot_config.pct_reinvest_profit
        self._logger = logger
        self._metrics_manager = metrics_manager
        self._notifications_manager = notifications_manager
        exchange = manager.get_exchange(bot_config.exchange_id)
        if not exchange:
            raise Exception(f"Cannot get Exchange from {bot_config.exchange_id} ID")
        self.exchange = exchange  # type: ignore
        self.exchange_manager = exchange_manager

        precision_amount = int(self.exchange_manager.get_precision_amount(self.exchange, self.pair))
        precision_price = int(self.exchange_manager.get_precision_price(self.exchange, self.pair))
        self._bot_status_logic = BotStatusLogic(logger, metrics_manager, notifications_manager, precision_amount, precision_price)
        self.status.budget.precision_price = precision_price

        self._order_book_cache = None

        self._update_orders_status()

    def new_trade_manual(self, size: float, entry_price: float, exit_order_id, exit_price: float) -> str:
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
        new_trade.id = str(int(time.time() * 1000))  # TODO: improve trade.id auto generation
        new_trade.entry_cost = entry_price * size
        new_trade.entry_time = int(new_trade.id)
        self.status.active_trades.append(new_trade)
        return new_trade.id

    def _update_orders_status(self) -> BotStatus:
        # orders
        # update active and archived orders
        # call _update_trades_on_update_orders to update trades
        updated_orders = []
        for order in self.status.active_orders:
            # update order status
            updated_order = self.fetch_order(order.id)

            if updated_order:
                self.status = self._bot_status_logic.update_trades_on_update_orders(self.status, updated_order)
                if updated_order.status in [OrderStatusType.closed, OrderStatusType.canceled, OrderStatusType.rejected]:
                    # move to archived
                    self.status.archived_orders.append(updated_order)
                    # TODO:
                    #  - OrderStatusType.canceled, OrderStatusType.rejected is not considered
                    #  - now, only stop loss orders can be found closed, as we add limit buy and sell we should send correspondant metrics.
                    self._metrics_manager.counter(ORDER_STOP_LOSS_CLOSED, self.id, 1, [f"exchange:{self.bot_config.exchange_id.value}"])
                else:
                    # keep active with new status
                    updated_orders.append(updated_order)
            else:
                self._logger.error(f"The order {order.id} has disappear! This should only happened on test environments")

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
            self._logger.error("Error get_balance", exc_info=1)
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
            self._logger.error("Error reading candles: %s", err, exc_info=1)
            return pd.DataFrame()

    def limit_min_amount(self) -> Optional[float]:
        try:
            return self.exchange_manager.limit_min_amount(
                self.exchange,
                pair=self.pair,
            )
        except Exception as err:
            print(f"Error getting limit min amount: {err}")
            self._logger.error("Error getting limit min amount: %s", err, exc_info=1)
            return None

    def limit_min_cost(self) -> Optional[float]:
        try:
            return self.exchange_manager.limit_min_cost(
                self.exchange,
                pair=self.pair,
            )
        except Exception as err:
            print(f"Error getting limit min cost: {err}")
            self._logger.error("Error getting limit min cost: %s", err, exc_info=1)
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
            self._logger.error("Error getting amount to precision: %s", err, exc_info=1)
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
            self._logger.error("Error getting price to precision: %s", err, exc_info=1)
            return None

    def get_order_book(self, use_cache: bool = False) -> Optional[OrderBook]:
        if use_cache and self._order_book_cache:
            return self._order_book_cache

        try:
            order_book = self.exchange_manager.read_order_book(
                self.exchange,
                pair=self.pair,
            )
            self._order_book_cache = order_book
            return order_book
        except Exception as err:
            print(f"Error getting order book: {err}")
            self._logger.error("Error getting order book: %s", err, exc_info=1)
            return None

    #  ---- Orders operations
    def cancel_order(self, order_id: str) -> Optional[Order]:
        try:
            order = self.exchange_manager.cancel_order(
                self.exchange,
                bot_config=self.bot_config,
                order_id=order_id,
            )
            self._metrics_manager.counter(ORDER_CANCELLED, self.id, 1, [f"exchange:{self.bot_config.exchange_id.value}"])
            self._notifications_manager.low(f"Order {order_id} was cancelled by strategy.")
            self.status = self._bot_status_logic.archive_order_on_cancel(self.status, order)
            return order
        except Exception as err:
            print(f"Error cancelling order: {err}")
            self._logger.error(f"Error cancelling order {order_id}: %s", err, exc_info=1)
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
            self._logger.info("Placed stop loss: %s", order)
            self._metrics_manager.counter(ORDER_STOP_LOSS, self.id, 1, [f"exchange:{self.bot_config.exchange_id.value}"])
            self._notifications_manager.low(f"Placed stop loss: {order.id} for {order.amount} {order.pair.base}. Will trigger at {precision_stop_price} {order.pair.quote} stop at: {precision_price} {order.pair.quote}")

            self.status = self._bot_status_logic.register_new_order_on_trades(self.status, order)
            return order
        except Exception as err:
            print(f"Error creating stop loss: {err}")
            self._logger.error("Error creating stop loss: %s", err, exc_info=1)
            return None

    def create_limit_buy_order(self, amount, price) -> Optional[Order]:
        """buy (0.01 BTC at 47k USDT)  pair=BTC/UST"""
        raise NotImplementedError

    def create_limit_sell_order(self, amount, price) -> Optional[Order]:
        raise NotImplementedError

    def create_market_buy_order(self, amount: float) -> Optional[Order]:
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
            self._metrics_manager.counter(ORDER_BUY_MARKET, self.id, 1, [f"exchange:{self.bot_config.exchange_id.value}"])
            self._notifications_manager.low(f"Placed market buy: {order.id} for  {order.amount} {order.pair.base} at {order.average} {order.pair.quote} , spending: {order.cost}{order.pair.quote}")

            self.status = self._bot_status_logic.register_new_order_on_trades(self.status, order)
            return order
        except Exception as err:
            print(f"Error creating market buy order: {err}")
            self._logger.error("Error creating market buy order: %s", err, exc_info=1)
            return None

    def create_market_sell_order(self, amount: float, trades_to_close: List[Trade] = []) -> Optional[Order]:
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
            self._metrics_manager.counter(ORDER_SELL_MARKET, self.id, 1, [f"exchange:{self.bot_config.exchange_id.value}"])
            self._notifications_manager.low(f"Placed market sell: {order.id} for {order.amount} {order.pair.base} at {order.average} {order.pair.quote}, getting: {order.cost}{order.pair.quote}")

            for trade in trades_to_close:
                trade.exit_order_id = order.id
                trade.exit_time = order.timestamp
                trade.exit_price = order.average

            self.status = self._bot_status_logic.register_new_order_on_trades(self.status, order)
            return order
        except Exception as err:
            print(f"Error creating market sell order: {err}")
            self._logger.error("Error creating market sell order: %s", err, exc_info=1)
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
            self._logger.error("Error fetching order: %s", err, exc_info=1)
            return None



    def get_estimated_last_close(self) -> Optional[float]:
        # https://docs.ccxt.com/#/?id=ticker-structure
        # Although some exchanges do mix-in order book's top bid/ask prices into their tickers
        # (and some exchanges even serve top bid/ask volumes) you should not treat a ticker as a fetchOrderBook
        # replacement. The main purpose of a ticker is to serve statistical data, as such,
        # treat it as "live 24h OHLCV". It is known that exchanges discourage frequent fetchTicker requests by
        # imposing stricter rate limits on these queries. If you need a unified way to access bids and asks you
        # should use fetchL[123]OrderBook family instead.
        # The idea was to use fetch_ticker[close]

        order_book = self.get_order_book()
        try:
            # TODO order_book.bids and asks could be empty
            last_bid = order_book.bids[0].price
            last_ask = order_book.asks[0].price
            estimated_last_close = (last_bid + last_ask) / 2
            self._metrics_manager.gauge(ESTIMATED_LAST_CLOSE, self.id, estimated_last_close, ["indicator"])
            return estimated_last_close
        except Exception as err:  # noqa: F841
            return None

    def get_estimated_sell_price_from_cache(self) -> Optional[float]:
        # https://docs.ccxt.com/#/?id=ticker-structure
        order_book = self.get_order_book(use_cache=True)

        try:
            # TODO order_book.bids and asks could be empty
            estimated_sell_price = (order_book.bids[0].price + order_book.bids[1].price + order_book.bids[2].price) / 3
            self._metrics_manager.gauge(ESTIMATED_SALE_PRICE, self.id, estimated_sell_price, ["indicator"])

            return estimated_sell_price
        except Exception as err:  # noqa: F841
            return None
