from logging import Logger

from elena.domain.model.bot_config import BotConfig
from elena.domain.model.bot_status import BotStatus
from elena.domain.ports.bot import Bot
from elena.domain.ports.strategy_manager import StrategyManager


class TrailingStop(Bot):
    _manager: StrategyManager
    _logger: Logger
    _config: BotConfig
    _name: str

    def init(self, manager: StrategyManager, logger: Logger, bot_config: BotConfig):  # type: ignore
        self._manager = manager
        self._logger = logger
        self._config = bot_config
        self._name = self.__class__.__name__

    def next(self, status: BotStatus) -> BotStatus:
        self._logger.info("%s strategy: processing next cycle ...", self._name)
        return status
