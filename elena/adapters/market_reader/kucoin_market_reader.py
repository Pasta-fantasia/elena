import logging
from typing import Tuple

from elena.domain.model.Error import Error
from elena.domain.model.market_candles import MarketCandles
from elena.domain.model.time_period import TimePeriod
from elena.domain.model.trading_pair import TradingPair
from elena.domain.ports.emit_flesti import EmitFlesti
from elena.domain.ports.market_reader import MarketReader


class KuCoinMarketReader(MarketReader):

    def __init__(self, emit_flesti: EmitFlesti):
        self._emit_flesti = emit_flesti

    def read(self, pair: TradingPair, period: TimePeriod) -> Tuple[MarketCandles, Error]:
        logging.info('Read KuCoin market for pair %s', pair)
        # TODO Implement me!!
        return Error.none()