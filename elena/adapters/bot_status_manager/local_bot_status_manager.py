
from elena.domain.model.Error import Error
from elena.domain.model.bot_status import BotStatus
from elena.domain.ports.bot_status_manager import BotSpawner
from elena.domain.ports.config import Config
from elena.domain.ports.logger import Logger


class LocalBotSpawner(BotSpawner):

    def __init__(self, config: Config, logger: Logger):
        self._config = config
        self._logger = logger

    def load(self, bot_id: str) -> BotStatus:
        self._logger.info('Spawned %s bot', bot_id)
        # TODO Implement me!!
        return BotStatus(
            bot_id=bot_id,
            status={},
        )
        pass

    def write(self, status: BotStatus) -> Error:
        self._logger.info('Writing %s bot status to disk', status.bot_id)
        # TODO Implement me!!
        return Error.none()
