from typing import Tuple

from elena.domain.model.Error import Error
from elena.domain.model.market_candles import MarketCandles
from elena.domain.model.time_period import TimePeriod
from elena.domain.model.trading_pair import TradingPair
from elena.domain.ports.config import Config
from elena.domain.ports.logger import Logger
from elena.domain.ports.market_reader import MarketReader


class KuCoinMarketReader(MarketReader):

    def __init__(self, config: Config, logger: Logger):
        self._config = config
        self._logger = logger

    def read(self, pair: TradingPair, period: TimePeriod) -> Tuple[MarketCandles, Error]:
        self._logger.info('Read KuCoin market for pair %s', pair)
        # TODO Implement me!!
        return Error.none()
