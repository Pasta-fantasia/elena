import importlib
from datetime import datetime
from typing import List, Optional, Tuple

import pandas as pd
from cron_converter import Cron

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
            run, status = self._get_run_status(bot_config, previous_statuses_dict)
            if run:
                self._logger.info("Running bot %s: %s", bot_config.id, bot_config.name)
                updated_status = self._run_bot(status, bot_config)
                if updated_status:
                    updated_statuses.append(updated_status)
        return updated_statuses

    def _get_run_status(
            self, bot_config: BotConfig, previous_statuses_dict
    ) -> Tuple[bool, BotStatus]:
        run = True
        if bot_config.id in previous_statuses_dict:
            status = previous_statuses_dict[bot_config.id]
            last_execution = datetime.fromtimestamp(status.timestamp / 1000)
            if (
                    bot_config.cron_expression
            ):  # If there is no cron expression, the bot will run every time
                run = self._check_if_bot_has_to_run(
                    last_execution, bot_config.cron_expression
                )
        else:
            status = BotStatus(
                bot_id=bot_config.id,
                active_orders=[],
                archived_orders=[],
                active_trades=[],
                closed_trades=[],
            )
        return run, status

    @staticmethod
    def _check_if_bot_has_to_run(
            last_execution: datetime, cron_expression: str
    ) -> bool:
        """
        Checks if the bot has to run or not comparing with cron expression.
        :param last_execution: the datetime of previous execution
        :param cron_expression: the cron expression to check
        :return: True if the bot has to run, False otherwise
        """
        cron_instance = Cron(cron_expression)
        schedule = cron_instance.schedule(last_execution)
        schedule.next()
        next_execution = schedule.next()
        now = datetime.now()
        return next_execution <= now

    def _run_bot(self, status: BotStatus, bot_config: BotConfig) -> Optional[BotStatus]:
        bot = self._get_bot_instance(bot_config, status)
        exchange = self.get_exchange(bot_config.exchange_id)
        if not exchange:
            self._logger.error(
                "Bot %s: %s has no valid exchange configuration.",
                bot_config.id,
                bot_config.name,
            )
            return None
        #updated_order_status = self._update_orders_status(exchange, status, bot_config)
        return bot.next()

    def _get_bot_instance(self, bot_config: BotConfig, bot_status: BotStatus) -> Bot:
        class_parts = self._config.strategy_class.split(".")
        class_name = class_parts[-1]
        module_path = ".".join(class_parts[0:-1])
        module = importlib.import_module(module_path)
        _class = getattr(module, class_name)
        bot = _class()
        bot.init(manager=self, logger=self._logger, bot_config=bot_config, bot_status)
        return bot

    def get_exchange(self, exchange_id: ExchangeType) -> Optional[Exchange]:
        for exchange in self._exchanges:
            if exchange.id == exchange_id.value:
                return exchange
        return None



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

        amount = self.amount_to_precision(exchange, bot_config.pair, amount)
        stop_price = self.price_to_precision(exchange, bot_config.pair, stop_price)
        price = self.price_to_precision(exchange, bot_config.pair, price)

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

    def get_balance(self, exchange: Exchange) -> pd.DataFrame:
        return self._exchange_manager.get_balance(exchange)

    def read_candles(
            self,
            exchange: Exchange,
            pair: TradingPair,
            page_size: int,
            time_frame: TimeFrame = TimeFrame.min_1,  # type: ignore
    ) -> pd.DataFrame:
        # TODO User the new parameter page_size ... or remove it
        return self._exchange_manager.read_candles(exchange, pair, time_frame)

    def get_order_book(self) -> OrderBook:
        raise NotImplementedError


    def limit_min_amount(self, exchange: Exchange, pair: TradingPair) -> float:
        return self._exchange_manager.limit_min_amount(exchange, pair)

    def create_limit_buy_order(
            self, exchange: Exchange, bot_config: BotConfig, amount, price
    ) -> Order:
        raise NotImplementedError

    def create_limit_sell_order(
            self, exchange: Exchange, bot_config: BotConfig, amount, price
    ) -> Order:
        raise NotImplementedError

    def create_market_buy_order(
            self, exchange: Exchange, bot_config: BotConfig, amount: float
    ) -> Order:
        params = {"type": "spot"}

        amount = self.amount_to_precision(exchange, bot_config.pair, amount)
        order = self._exchange_manager.place_order(
            exchange=exchange,
            bot_config=bot_config,
            order_type=OrderType.market,  # type: ignore
            side=OrderSide.buy,  # type: ignore
            amount=amount,
            params=params,
        )
        self._logger.info("Placed market buy: %s", order)

        return order

    def create_market_sell_order(
            self, exchange: Exchange, bot_config: BotConfig, amount: float
    ) -> Order:
        params = {"type": "spot"}

        amount = self.amount_to_precision(exchange, bot_config.pair, amount)
        order = self._exchange_manager.place_order(
            exchange=exchange,
            bot_config=bot_config,
            order_type=OrderType.market,  # type: ignore
            side=OrderSide.sell,  # type: ignore
            amount=amount,
            params=params,
        )
        self._logger.info("Placed market buy: %s", order)

        return order

    def fetch_order(self, exchange: Exchange, bot_config: BotConfig, order_id: str) -> Order:
        return self._exchange_manager.fetch_order(exchange, bot_config, order.id)

    def amount_to_precision(
            self, exchange: Exchange, pair: TradingPair, amount: float
    ) -> float:
        return self._exchange_manager.amount_to_precision(exchange, pair, amount)

    def price_to_precision(
            self, exchange: Exchange, pair: TradingPair, price: float
    ) -> float:
        return self._exchange_manager.price_to_precision(exchange, pair, price)
