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
        self._path = pathlib.Path(config["LocalBotManager"]["path"])
        self._logger = logger
        Path(self._path).mkdir(parents=True, exist_ok=True)
        logger.info("LocalBotManager working at %s", self._path)

    def load_all(self, strategy_config: StrategyConfig) -> List[BotStatus]:
        statuses = []
        for bot in strategy_config.bots:
            status = self.load(bot.id)
            if status:
                statuses.append(status)
        return statuses

    def load(self, bot_id: str) -> Optional[BotStatus]:
        filename = self._filename(bot_id)
        self._logger.debug("Reading bot status from disk: %s", filename)
        try:
            with open(filename, "rb") as f:
                status = pickle.load(f)
        except FileNotFoundError:
            return None
        self._logger.debug(
            "Read bot status %s with %d orders", bot_id, len(status.active_orders)
        )
        return status

    def write_all(self, statuses: List[BotStatus]):
        for status in statuses:
            self.write(status)

    def write(self, status: BotStatus):
        if not status:
            return
        filename = self._filename(status.bot_id)
        self._logger.debug("Writing bot status to disk: %s", filename)
        with open(filename, "wb") as f:
            pickle.dump(status, f, pickle.HIGHEST_PROTOCOL)
        self._logger.debug(
            "Wrote bot status %s with %d orders",
            status.bot_id,
            len(status.active_orders),
        )

    def _filename(self, id: str):
        return path.join(self._path, f"{id}.pickle")
