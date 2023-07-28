from logging import Logger

from elena.domain.ports.bot import Strategy


class TrailingStop(Strategy):

    def __init__(self,
                 logger: Logger,
                 ):
        self._logger = logger

    def next(self):
        pass
