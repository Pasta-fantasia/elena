from typing import Protocol, List, Optional

from elena.domain.model.bot_status import BotStatus
from elena.domain.model.strategy_config import StrategyConfig


class BotManager(Protocol):

    def load_all(self, strategy_config: StrategyConfig) -> List[BotStatus]:
        """
        Loads all bot statuses pertaining to a Strategy from persistence
        :param strategy_config: the strategy configuration
        :return: the list of bot statuses, or error if any
        """
        pass

    def load(self, bot_id: str) -> Optional[BotStatus]:
        """
        Loads a bot status from persistence
        :param bot_id: the bot identifier
        :return: the bot status, or error if any
        """
        pass

    def write_all(self, statuses: List[BotStatus]):
        """
        Persists all the bot statuses
        :param statuses: a list of bot status
        :return: error if any
        """
        pass

    def write(self, status: BotStatus):
        """
        Persists the status of a bot
        :param status: the bot status
        :return: error if any
        """
        pass
