from logging import Logger

from elena.domain.model.bot_config import BotConfig
from elena.domain.model.bot_status import BotStatus
from elena.domain.ports.strategy import Strategy
from elena.domain.ports.strategy_manager import StrategyManager


class TrailingStop(Strategy):
    _manager: StrategyManager
    _logger: Logger

    def init(self, manager: StrategyManager):
        self._manager = manager
        self._logger = manager.get_logger()
        self._name = self.__class__.__name__

    def next(self, status: BotStatus, bot_config: BotConfig) -> BotStatus:
        self._logger.info('%s strategy: processing next cycle ...', self._name)
        return status
