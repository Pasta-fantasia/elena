from typing import Protocol

import pandas as pd

from elena.domain.model.exchange import Exchange
from elena.domain.model.time_frame import TimeFrame
from elena.domain.model.trading_pair import TradingPair


class MarketReader(Protocol):

    def read_candles(self, exchange: Exchange, pair: TradingPair, time_frame: TimeFrame) -> pd.DataFrame:
        """
        Reads market candles
        :param exchange: exchange where to read market data
        :param pair: trading pair to read
        :param time_frame: time frame to read
        :return: the market candles
        """
        pass
