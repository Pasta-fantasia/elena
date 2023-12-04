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
    status: BotStatus
    _logger: Logger

    def _update_orders_status(self, exchange: Exchange, status: BotStatus, bot_config: BotConfig) -> BotStatus:
        # orders
        updated_orders = []
        for order in status.active_orders:
            # update status
            updated_order = self.fetch_order(exchange, bot_config, order.id)

            if (updated_order.status == OrderStatusType.closed or updated_order.status == OrderStatusType.canceled):
                # notify
                if updated_order.status == OrderStatusType.closed:
                    # TODO: [Pere] "self._logger.info(f"Notify!" it's where a notification should be sent to the user.
                    #  Where we should push or connect to telegram... we can have it read only first.
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
            elif (
                    updated_order.status == OrderStatusType.open
                    and updated_order
                    and updated_order.filled > 0  # type: ignore
            ):
                # TODO: [Fran] How to manage partially filled orders? Should we wait and see?
                #  Should we notify and do nothing waiting for the user to act?
                self._logger.info(
                    f"Notify! Order {updated_order.id} is PARTIALLY_FILLED filled: {updated_order.filled} "
                    f"of {updated_order.amount} {updated_order.pair} at {updated_order.average}"
                )
                self.cancel_order(
                    exchange=exchange,
                    bot_config=bot_config,
                    order_id=order.id,
                )
                # TODO: [Pere] I'm using orders and trades as pure lists...
                #              should we have a layer on top? Not a priority.
                # TODO: [Fran] is this "update" equal for partials? refactor?
                # updates trades
                for trade in status.active_trades:
                    if trade.exit_order_id == updated_order.id:
                        status.active_trades.remove(trade)
                        trade.exit_time = updated_order.timestamp
                        trade.exit_price = updated_order.average
                        status.closed_trades.append(trade)
                # move to archived
                status.archived_orders.append(updated_order)
            else:
                updated_orders.append(updated_order)

        status.active_orders = updated_orders

        return status

    def init(self, manager: StrategyManager, logger: Logger, bot_config: BotConfig, bot_status: BotStatus):
        self.id = bot_config.id
        self.name = bot_config.name
        self.pair = bot_config.pair
        self.time_frame = bot_config.time_frame
        self.config = bot_config.config
        self.manager = manager
        self.bot_config = bot_config
        self.status = bot_status
        self._logger = logger

        exchange = manager.get_exchange(bot_config.exchange_id)
        if not exchange:
            raise Exception(f"Cannot get Exchange from {bot_config.exchange_id} ID")
        self.exchange = exchange  # type: ignore

    def next(self) -> Optional[BotStatus]:
        ...

    #  ---- Information

    def get_balance(self) -> Optional[Balance]:
        try:
            return self.exchange.get_balance(self.exchange)
        except Exception as err:
            self._logger.error(f"Error getting balance: {err}", error=err)
            return None

    def read_candles(
        self, page_size: int = 100, time_frame: Optional[TimeFrame] = None
    ) -> pd.DataFrame:
        if not time_frame:
            time_frame = self.time_frame
        try:
            # TODO User the new parameter page_size ... or remove it
            return self.exchange.read_candles(
                self.exchange,
                self.pair,
                page_size,
                time_frame,
            )
        except Exception as err:
            self._logger.error(f"Error reading candles: {err}", error=err)
            return pd.DataFrame()


    def limit_min_amount(self) -> Optional[float]:
        try:
            return self.exchange.limit_min_amount(
                self.exchange,
                self.pair,
            )
        except Exception as err:
            self._logger.error(f"Error getting limit min amount: {err}", error=err)
            return None

    def amount_to_precision(self, amount: float) -> float:
        return self.exchange.amount_to_precision(self.exchange, self.pair, amount)

    def price_to_precision(self, price: float) -> float:
        return self.exchange.price_to_precision(self.exchange, self.pair, price)

    def get_order_book(self) -> Optional[OrderBook]:
        try:
            return self.exchange.get_order_book()
        except Exception as err:
            self._logger.error(f"Error getting order book: {err}", error=err)
            return None

    #  ---- Orders operations
    def cancel_order(self, order_id: str) -> Optional[Order]:
        try:
            return self.exchange.cancel_order(self.exchange, self.bot_config, order_id)
        except Exception as err:
            self._logger.error(f"Error cancelling order {order_id}: {err}", error=err)
            return None

    def stop_loss(self, amount: float, stop_price: float, price: float) -> Optional[Order]:
        try:
            amount = self.amount_to_precision(self.exchange, self.pair, amount)
            stop_price = self.price_to_precision(self.exchange, self.pair, stop_price)
            price = self.price_to_precision(self.exchange, self.pair, price)

            params = {"type": "spot", "triggerPrice": stop_price, "timeInForce": "GTC"}

            order = self.exchange.place_order(
                exchange=self.exchange,
                bot_config=self.bot_config,
                order_type=OrderType.limit,  # type: ignore
                side=OrderSide.sell,  # type: ignore
                amount=amount,
                price=price,
                params=params,
            )
            self._logger.info("Placed market stop loss: %s", order)

            return order
        except Exception as err:
            self._logger.error(f"Error creating stop loss: {err}", error=err)
            return None


    def create_limit_buy_order(self, amount, price) -> Optional[Order]:
        """buy (0.01 BTC at 47k USDT)  pair=BTC/UST"""
        raise NotImplementedError

    def create_limit_sell_order(self, amount, price) -> Optional[Order]:
        raise NotImplementedError

    def create_market_buy_order(self, amount) -> Optional[Order]:
        try:
            params = {"type": "spot"}

            amount = self.amount_to_precision(self.exchange, self.pair, amount)
            order = self.exchange.place_order(
                exchange=self.exchange,
                bot_config=self.bot_config,
                order_type=OrderType.market,  # type: ignore
                side=OrderSide.buy,  # type: ignore
                amount=amount,
                params=params,
            )
            self._logger.info("Placed market buy: %s", order)

            return order
        except Exception as err:
            self._logger.error(f"Error creating market buy order: {err}", error=err)
            return None

    def create_market_sell_order(self, amount) -> Optional[Order]:
        try:
            params = {"type": "spot"}

            amount = self.amount_to_precision(self.exchange, self.pair, amount)
            order = self.exchange.place_order(
                exchange=self.exchange,
                bot_config=self.bot_config,
                order_type=OrderType.market,  # type: ignore
                side=OrderSide.sell,  # type: ignore
                amount=amount,
                params=params,
            )
            self._logger.info("Placed market buy: %s", order)

            return order
        except Exception as err:
            self._logger.error(f"Error creating market sell order: {err}", error=err)
            return None

    def fetch_order(self, order_id: str) -> Optional[Order]:
        try:
            return self.exchange.fetch_order(
                self.exchange,
                self.bot_config,
                order_id,
            )
        except Exception as err:
            self._logger.error(f"Error fetching order: {err}", error=err)
            return None
