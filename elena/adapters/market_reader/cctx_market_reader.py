from typing import Dict, List

import ccxt
import pandas as pd

from elena.domain.model.exchange import Exchange, ExchangeType
from elena.domain.model.time_frame import TimeFrame
from elena.domain.model.trading_pair import TradingPair
from elena.domain.ports.logger import Logger
from elena.domain.ports.market_reader import MarketReader


class CctxMarketReader(MarketReader):
    _connect_mapper = {
        ExchangeType.bitget: ccxt.bitget,
        ExchangeType.kucoin: ccxt.kucoin
    }

    def __init__(self, config: Dict, logger: Logger):
        self._config = config['CctxMarketReader']
        self._logger = logger

    def read_candles(self, exchange: Exchange, pair: TradingPair, time_frame: TimeFrame) -> pd.DataFrame:
        self._logger.debug('Reading market from %s with CCTX for pair %s ...', exchange.id, pair)

        connection = self._connect(exchange)
        candles = self._fetch(connection, pair, time_frame)
        self._logger.info('Read %d %s candles from %s', candles.shape[0], pair, exchange.id.value)
        return candles

    def _connect(self, exchange: Exchange):
        return self._connect_mapper[exchange.id]({
            'apiKey': exchange.api_key,
            'secret': exchange.secret,
            'password': exchange.password,
        })

    def _fetch(self, connection, pair: TradingPair, time_frame: TimeFrame) -> pd.DataFrame:
        candles_list = self._fetch_with_retry(connection, pair, time_frame)
        candles_df = pd.DataFrame(candles_list)
        candles_df.columns = ['Open time', 'Open', 'High', 'Low', 'Close', 'Volume']
        candles_df["Open time"] = pd.to_numeric(candles_df["Open time"], downcast="integer")
        candles_df["Open"] = pd.to_numeric(candles_df["Open"], downcast="float")
        candles_df["High"] = pd.to_numeric(candles_df["High"], downcast="float")
        candles_df["Low"] = pd.to_numeric(candles_df["Low"], downcast="float")
        candles_df["Close"] = pd.to_numeric(candles_df["Close"], downcast="float")
        candles_df["Volume"] = pd.to_numeric(candles_df["Volume"], downcast="float")
        candles_df.set_index('Open time')
        return candles_df

    def _fetch_with_retry(self, connection, pair: TradingPair, time_frame: TimeFrame) -> List[List]:
        # https://github.com/ccxt/ccxt/issues/10273
        # from https://github.com/ccxt/ccxt/blob/master/examples/py/kucoin-rate-limit.py
        i = 0
        retry = True
        candles = pd.DataFrame()
        while retry:
            try:
                candles = connection.fetch_ohlcv(str(pair), time_frame.value, limit=self._config['limit'])
                self._logger.debug('Fetched %d %s %d candles from %s to %s',
                                   len(candles),
                                   str(pair),
                                   time_frame,
                                   connection.iso8601(candles[0][0]),
                                   connection.iso8601(candles[len(candles) - 1][0])
                                   )
                retry = False
            except ccxt.RateLimitExceeded as e:
                self._logger.info('Retrying connection to exchange, %s: %s', type(e).__name__, e)
                connection.sleep(self._config['retry_every_milliseconds'])
            except Exception as err:
                raise err
            i += 1
        return candles
