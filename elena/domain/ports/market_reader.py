from typing import Protocol, Tuple

from elena.domain.model.Error import Error
from elena.domain.model.market_candles import MarketCandles
from elena.domain.model.time_period import TimePeriod
from elena.domain.model.trading_pair import TradingPair


class MarketReader(Protocol):

    def read(self, pair: TradingPair, period: TimePeriod) -> Tuple[MarketCandles, Error]:
        """
        Reads market status
        :param pair: trading pair to read
        :param period: time period to read
        :return: tha market status, and error if any
        """
        pass
