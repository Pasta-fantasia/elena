from typing import Dict, List, Protocol, runtime_checkable

from elena.domain.model.bot_status import BotStatus
from elena.domain.model.strategy_config import StrategyConfig
from elena.domain.ports.logger import Logger
from elena.domain.ports.storage_manager import StorageManager


@runtime_checkable
class BotManager(Protocol):
    def init(
        self,
        config: Dict,
        logger: Logger,
        storage_manager: StorageManager,
    ):
        ...

    def load_all(self, strategy_config: StrategyConfig) -> List[BotStatus]:
        """
        Loads all bot statuses pertaining to a Strategy from persistence
        :param strategy_config: the strategy configuration
        :return: the list of bot statuses, or error if any
        """
        ...

    def save_all(self, statuses: List[BotStatus]):
        """
        Persists all the bot statuses
        :param statuses: a list of bot status
        :return: error if any
        """
        ...
