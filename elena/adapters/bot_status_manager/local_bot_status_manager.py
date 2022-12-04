import logging

from elena.domain.model.Error import Error
from elena.domain.model.bot_status import BotStatus
from elena.domain.ports.bot_status_manager import BotSpawner


class LocalBotSpawner(BotSpawner):

    def __init__(self):
        pass

    def load(self, bot_id: str) -> BotStatus:
        logging.info('Spawned %s bot', bot_id)
        # TODO Implement me!!
        return BotStatus(
            bot_id=bot_id,
            status={},
        )
        pass

    def write(self, status: BotStatus) -> Error:
        logging.info('Writing %s bot status to disk', status.bot_id)
        # TODO Implement me!!
        return Error.none()
