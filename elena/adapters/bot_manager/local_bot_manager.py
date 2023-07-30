import pathlib
import pickle
from os import path
from pathlib import Path
from typing import Dict, List, Optional

from elena.domain.model.bot_status import BotStatus
from elena.domain.model.strategy_config import StrategyConfig
from elena.domain.ports.bot_manager import BotManager
from elena.domain.ports.logger import Logger


class LocalBotManager(BotManager):

    def __init__(self, config: Dict, logger: Logger):
        self._path = pathlib.Path(config['LocalBotManager']['path'])
        self._logger = logger
        Path(self._path).mkdir(parents=True, exist_ok=True)
        logger.info("LocalBotManager working at %s", self._path)

    def load_all(self, strategy_config: StrategyConfig) -> List[BotStatus]:
        _statuses = []
        for _bot in strategy_config.bots:
            _status = self.load(_bot.id)
            if _status:
                _statuses.append(_status)
        return _statuses

    def load(self, bot_id: str) -> Optional[BotStatus]:
        _filename = self._filename(bot_id)
        self._logger.debug('Reading bot status from disk: %s', _filename)
        try:
            with open(_filename, 'rb') as f:
                _status = pickle.load(f)
        except FileNotFoundError:
            return None
        self._logger.debug('Read bot status %s with %d orders', bot_id, len(_status.orders))
        return _status

    def write_all(self, statuses: List[BotStatus]):
        for status in statuses:
            self.write(status)

    def write(self, status: BotStatus):
        if not status:
            return
        _filename = self._filename(status.bot_id)
        self._logger.debug('Writing bot status to disk: %s', _filename)
        with open(_filename, 'wb') as f:
            pickle.dump(status, f, pickle.HIGHEST_PROTOCOL)
        self._logger.debug('Wrote bot status %s with %d orders', status.bot_id, len(status.orders))

    def _filename(self, id: str):
        return path.join(self._path, f'{id}.pickle')
