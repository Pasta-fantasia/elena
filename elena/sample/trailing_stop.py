from logging import Logger

from elena.domain.model.bot_config import BotConfig
from elena.domain.model.bot_status import BotStatus
from elena.domain.ports.bot import Bot
from elena.domain.ports.strategy_manager import StrategyManager


class TrailingStop(Bot):
    _manager: StrategyManager
    _logger: Logger
    _name: str

    def init(self, manager: StrategyManager, logger: Logger):
        self._manager = manager
        self._logger = logger
        self._name = self.__class__.__name__

    def next(self, status: BotStatus, bot_config: BotConfig) -> BotStatus:
        self._logger.info('%s strategy: processing next cycle ...', self._name)
        return status
