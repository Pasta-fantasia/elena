from typing import Protocol

from elena.domain.model.Error import Error
from elena.domain.model.bot_status import BotStatus


class BotStatusManager(Protocol):

    def load(self, bot_id: str) -> BotStatus:
        pass

    def write(self, status: BotStatus) -> Error:
        """
        Persists the status of a bot
        :param status: the bot status
        :return: error if any
        """
        pass
