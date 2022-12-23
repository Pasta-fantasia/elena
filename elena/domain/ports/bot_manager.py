from typing import Protocol, List

from elena.domain.model.bot_status import BotStatus


class BotManager(Protocol):

    def load(self, bot_id: str) -> BotStatus:
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
