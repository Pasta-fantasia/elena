import importlib
import typing as t
from typing import List

import pandas as pd

from elena.domain.model.balance import Balance
from elena.domain.model.bot_config import BotConfig
from elena.domain.model.bot_status import BotStatus
from elena.domain.model.exchange import Exchange, ExchangeType
from elena.domain.model.order import (Order, OrderSide, OrderStatusType,
                                      OrderType)
from elena.domain.model.order_book import OrderBook
from elena.domain.model.strategy_config import StrategyConfig
from elena.domain.model.time_frame import TimeFrame
from elena.domain.model.trading_pair import TradingPair
from elena.domain.ports.bot import Bot
from elena.domain.ports.bot_manager import BotManager
from elena.domain.ports.exchange_manager import ExchangeManager
from elena.domain.ports.logger import Logger
from elena.domain.ports.strategy_manager import StrategyManager


class StrategyManagerImpl(StrategyManager):
    def __init__(
        self,
        strategy_config: StrategyConfig,
        logger: Logger,
        bot_manager: BotManager,
        exchange_manager: ExchangeManager,
        exchanges: List[Exchange],
    ):
        self._config = strategy_config
        self._logger = logger
        self._bot_manager = bot_manager
        self._exchange_manager = exchange_manager
        self._exchanges = exchanges

    def run(self, previous_statuses: List[BotStatus]) -> List[BotStatus]:
        """
        Runs all strategy bots.
        A Bot is an instance of a strategy with a certain configuration
          1. retrieves the bot status of the previous execution with BotManager
          2. read info from market to define orders with ExchangeManager
          3. run the strategy logic to decide what to do (buy, sell, wait ...)
          4. once decided, if any, write orders to an Exchange with OrderManager
        :param previous_statuses: the list of all bot statuses from previous execution
        :return: the updated statuses list of all bot with any update in the current cycle
        """

        previous_statuses_dict = {
            _status.bot_id: _status for _status in previous_statuses
        }
        updated_statuses = []
        for bot_config in self._config.bots:
            self._logger.info("Running bot %s: %s", bot_config.id, bot_config.name)
            if bot_config.id in previous_statuses:
                status = previous_statuses_dict[bot_config.id]
            else:
                status = BotStatus(
                    bot_id=bot_config.id,
                    active_orders=[],
                    archived_orders=[],
                    active_trades=[],
                    closed_trades=[],
                )

            updated_status = self._run_bot(status, bot_config)
            if updated_status:
                updated_statuses.append(updated_status)
        return updated_statuses

    def _run_bot(
        self, status: BotStatus, bot_config: BotConfig
    ) -> t.Optional[BotStatus]:

        bot = self._get_bot_instance(bot_config)
        exchange = self.get_exchange(bot_config.exchange_id)
        if not exchange:
            self._logger.error("Bot %s: %s has no valid exchange configuration.", bot_config.id, bot_config.name)
            return None
        updated_order_status = self._update_orders_status(exchange, status, bot_config)
        status = bot.next(updated_order_status)
        return status

    def _get_bot_instance(self, bot_config: BotConfig) -> Bot:
        class_parts = self._config.strategy_class.split(".")
        class_name = class_parts[-1]
        module_path = ".".join(class_parts[0:-1])
        module = importlib.import_module(module_path)
        _class = getattr(module, class_name)
        bot = _class()
        bot.init(manager=self, logger=self._logger, bot_config=bot_config)
        return bot

    def get_exchange(self, exchange_id: ExchangeType) -> t.Optional[Exchange]:
        for exchange in self._exchanges:
            if exchange.id == exchange_id.value:
                return exchange
        return None

    def cancel_order(
        self, exchange: Exchange, bot_config: BotConfig, order_id: str
    ) -> Order:
        order = self._exchange_manager.cancel_order(
            exchange=exchange, bot_config=bot_config, order_id=order_id
        )
        self._logger.info("Canceled order: %s", order_id)
        return order

    def buy(self):
        self._logger.error("buy is not implemented")

    def sell(self):
        self._logger.error("sell is not implemented")

    def stop_loss_limit(
        self,
        exchange: Exchange,
        bot_config: BotConfig,
        amount: float,
        stop_price: float,
        price: float,
    ) -> Order:
        # https://docs.ccxt.com/#/README?id=stop-loss-orders
        # binance only accept stop_loss_limit for BTC/USDT

        params = {"type": "spot", "triggerPrice": stop_price, "timeInForce": "GTC"}

        order = self._exchange_manager.place_order(
            exchange=exchange,
            bot_config=bot_config,
            order_type=OrderType.limit,  # type: ignore
            side=OrderSide.sell,  # type: ignore
            amount=amount,
            price=price,
            params=params,
        )
        self._logger.info("Placed market stop loss: %s", order)

        return order

    def get_balance(self, exchange: Exchange) -> Balance:
        return self._exchange_manager.get_balance(exchange)

    def read_candles(
        self,
        exchange: Exchange,
        pair: TradingPair,
        time_frame: TimeFrame = TimeFrame.min_1,  # type: ignore
    ) -> pd.DataFrame:
        return self._exchange_manager.read_candles(exchange, pair, time_frame)

    def get_order_book(self) -> OrderBook:
        ...

    def _update_orders_status(
        self, exchange: Exchange, status: BotStatus, bot_config: BotConfig
    ) -> BotStatus:
        # orders
        updated_orders = []
        for order in status.active_orders:
            # update status
            updated_order = self._exchange_manager.fetch_order(
                exchange, bot_config, order.id
            )
            if (
                updated_order.status == OrderStatusType.closed
                or updated_order.status == OrderStatusType.canceled
            ):
                # notify
                if updated_order.status == OrderStatusType.closed:
                    # TODO: [Pere] "self._logger.info(f"Notify!" it's where a notification should be sent to the user.
                    #  Where we should push or connect to telegram... we can have it read only first.
                    self._logger.info(
                        f"Notify! Order {updated_order.id} was closed for {updated_order.amount} {updated_order.pair} "
                        f"at {updated_order.average}"
                    )
                if updated_order.status == OrderStatusType.canceled:
                    self._logger.info(
                        f"Notify! Order {updated_order.id} was cancelled!-"
                    )
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

    def limit_min_amount(self, exchange: Exchange, pair: TradingPair) -> float:
        return self._exchange_manager.limit_min_amount(exchange, pair)

    def amount_to_precision(
        self, exchange: Exchange, pair: TradingPair, amount: float
    ) -> float:
        return self._exchange_manager.amount_to_precision(exchange, pair, amount)

    def price_to_precision(
        self, exchange: Exchange, pair: TradingPair, price: float
    ) -> float:
        return self._exchange_manager.price_to_precision(exchange, pair, price)
