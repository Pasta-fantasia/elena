from typing import Dict, List, Optional, Protocol, runtime_checkable

from elena.domain.model.bot_status import BotStatus
from elena.domain.model.strategy_config import StrategyConfig
from elena.domain.ports.logger import Logger
from elena.domain.ports.metrics_manager import MetricsManager
from elena.domain.ports.notifications_manager import NotificationsManager


@runtime_checkable
class BotManager(Protocol):
    def init(
        self,
        config: Dict,
        logger: Logger,
        metrics_manager: MetricsManager,
        notifications_manager: NotificationsManager,
    ):
        ...

    def load_all(self, strategy_config: StrategyConfig) -> List[BotStatus]:
        """
        Loads all bot statuses pertaining to a Strategy from persistence
        :param strategy_config: the strategy configuration
        :return: the list of bot statuses, or error if any
        """
        ...

    def load(self, bot_id: str) -> Optional[BotStatus]:
        """
        Loads a bot status from persistence
        :param bot_id: the bot identifier
        :return: the bot status, or error if any
        """
        ...

    def write_all(self, statuses: List[BotStatus]):
        """
        Persists all the bot statuses
        :param statuses: a list of bot status
        :return: error if any
        """
        ...

    def write(self, status: BotStatus):
        """
        Persists the status of a bot
        :param status: the bot status
        :return: error if any
        """
        ...
