import pathlib
from pathlib import Path
from typing import Dict

from elena.domain.model.Error import Error
from elena.domain.model.bot_status import BotStatus
from elena.domain.ports.bot_manager import BotManager
from elena.domain.ports.logger import Logger


class LocalBotManager(BotManager):

    def __init__(self, config: Dict, logger: Logger):
        self._path = pathlib.Path(config['LocalBotManager']['path'])
        self._logger = logger
        Path(self._path).mkdir(parents=True, exist_ok=True)
        print(f"LocalBotManager working at {self._path}")

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
