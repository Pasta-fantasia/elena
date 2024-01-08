import os
import time
from datetime import datetime
from typing import List, Optional, Tuple

from cron_converter import Cron

from elena.domain.model.bot_config import BotConfig
from elena.domain.model.bot_status import BotStatus, BotBudget
from elena.domain.model.exchange import Exchange, ExchangeType
from elena.domain.model.strategy_config import StrategyConfig
from elena.domain.ports.bot import Bot
from elena.domain.ports.bot_manager import BotManager
from elena.domain.ports.exchange_manager import ExchangeManager
from elena.domain.ports.logger import Logger
from elena.domain.ports.metrics_manager import MetricsManager
from elena.domain.ports.notifications_manager import NotificationsManager
from elena.domain.ports.strategy_manager import StrategyManager
from elena.shared.dynamic_loading import get_class


class StrategyManagerImpl(StrategyManager):
    def __init__(
        self,
        strategy_config: StrategyConfig,
        logger: Logger,
        metrics_manager: MetricsManager,
        notifications_manager: NotificationsManager,
        bot_manager: BotManager,
        exchange_manager: ExchangeManager,
        exchanges: List[Exchange],
    ):
        self._config = strategy_config
        self._logger = logger
        self._metrics_manager = metrics_manager
        self._notifications_manager = notifications_manager
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

        previous_statuses_dict = {_status.bot_id: _status for _status in previous_statuses}
        updated_statuses = []
        for bot_config in self._config.bots:
            run, status = self._get_run_status(bot_config, previous_statuses_dict)
            if run:
                self._logger.info("Running bot %s: %s", bot_config.id, bot_config.name)
                try:
                    updated_status = self._run_bot(self._exchange_manager, bot_config, status)
                    if updated_status:
                        updated_statuses.append(updated_status)
                except Exception as err:
                    # A bad implemented bot should never crash Elena.
                    # The other bot may work and may need to do operations
                    self._logger.error("Unhandled exception", exc_info=1)
                    # Except we are on a test session.
                    if "PYTEST_CURRENT_TEST" in os.environ:
                        raise err
        return updated_statuses

    def _get_run_status(self, bot_config: BotConfig, previous_statuses_dict) -> Tuple[bool, BotStatus]:
        run = True
        if bot_config.id in previous_statuses_dict:
            status = previous_statuses_dict[bot_config.id]
            last_execution = datetime.fromtimestamp(status.timestamp / 1000)
            if bot_config.cron_expression:  # If there is no cron expression, the bot will run every time
                run = self._check_if_bot_has_to_run(last_execution, bot_config.cron_expression)
        else:
            status = BotStatus(
                bot_id=bot_config.id,
                active_orders=[],
                archived_orders=[],
                active_trades=[],
                closed_trades=[],
                budget=BotBudget()
            )
        return run, status

    @staticmethod
    def _check_if_bot_has_to_run(last_execution: datetime, cron_expression: str) -> bool:
        """
        Checks if the bot has to run or not comparing with cron expression.
        :param last_execution: the datetime of previous execution
        :param cron_expression: the cron expression to check
        :return: True if the bot has to run, False otherwise
        """
        cron_instance = Cron(cron_expression)
        schedule = cron_instance.schedule(last_execution)
        next_execution = schedule.next()
        now = datetime.now()
        return next_execution <= now

    def _run_bot(
        self,
        exchange_manager: ExchangeManager,
        bot_config: BotConfig,
        bot_status: BotStatus,
    ) -> Optional[BotStatus]:
        bot_status.timestamp = int(time.time() * 1000)
        bot = self._get_bot_instance(exchange_manager, bot_config, bot_status)
        return bot.next()

    def _get_bot_instance(
        self,
        exchange_manager: ExchangeManager,
        bot_config: BotConfig,
        bot_status: BotStatus,
    ) -> Bot:
        _class = get_class(self._config.strategy_class)
        bot = _class()
        bot.init(
            manager=self,
            logger=self._logger,
            metrics_manager=self._metrics_manager,
            notifications_manager=self._notifications_manager,
            exchange_manager=exchange_manager,
            bot_config=bot_config,
            bot_status=bot_status,
        )
        return bot

    def get_exchange(self, exchange_id: ExchangeType) -> Optional[Exchange]:
        for exchange in self._exchanges:
            if exchange.id == exchange_id.value:
                return exchange
        return None
