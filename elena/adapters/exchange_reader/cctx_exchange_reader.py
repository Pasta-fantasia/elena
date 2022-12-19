import time
from typing import Dict, List, Set

import ccxt
import pandas as pd

from elena.adapters.common import common_cctx
from elena.domain.model.balance import Balance, ByAvailability, ByCurrency
from elena.domain.model.currency import Currency
from elena.domain.model.exchange import Exchange
from elena.domain.model.order_book import OrderBook, PriceAmount
from elena.domain.model.time_frame import TimeFrame
from elena.domain.model.trading_pair import TradingPair
from elena.domain.ports.exchange_reader import ExchangeReader
from elena.domain.ports.logger import Logger


class CctxExchangeReader(ExchangeReader):

    def __init__(self, config: Dict, logger: Logger):
        self._config = config['CctxExchangeReader']
        self._logger = logger

    def read_candles(
            self,
            exchange: Exchange,
            pair: TradingPair,
            time_frame: TimeFrame = TimeFrame.min_1
    ) -> pd.DataFrame:
        self._logger.debug('Reading exchange candles from %s with CCTX for pair %s ...', exchange.id, pair)
        _conn = common_cctx.connect(exchange, self._logger)
        _candles = self._fetch_candles(_conn, pair, time_frame)
        self._logger.info('Read %d %s candles from %s', _candles.shape[0], pair, exchange.id.value)
        return _candles

    def _fetch_candles(self, connection, pair: TradingPair, time_frame: TimeFrame) -> pd.DataFrame:
        candles_list = self._fetch_candles_with_retry(connection, pair, time_frame)
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

    def _fetch_candles_with_retry(self, connection, pair: TradingPair, time_frame: TimeFrame) -> List[List]:
        # https://github.com/ccxt/ccxt/issues/10273
        # from https://github.com/ccxt/ccxt/blob/master/examples/py/kucoin-rate-limit.py
        i = 0
        _retry = True
        _candles = pd.DataFrame()
        while _retry:
            try:
                _candles = connection.fetch_ohlcv(str(pair), time_frame.value, limit=self._config['fetch_ohlcv_limit'])
                _retry = False
            except ccxt.RateLimitExceeded as e:
                self._logger.info('Retrying connection to exchange, %s: %s', type(e).__name__, e)
                connection.sleep(self._config['fetch_ohlcv_limit_retry_every_milliseconds'])
            except Exception as err:
                raise err
            i += 1
        return _candles

    def read_order_book(
            self,
            exchange: Exchange,
            pair: TradingPair
    ) -> OrderBook:
        self._logger.debug('Reading exchange order book from %s with CCTX for pair %s ...', exchange.id, pair)

        _conn = common_cctx.connect(exchange, self._logger)
        _ob = self._fetch_order_book(_conn, pair)
        self._logger.info('Read %d bids and %d asks for %s from %s', len(_ob.bids), len(_ob.asks), pair,
                          exchange.id.value)
        return _ob

    def _fetch_order_book(self, connection, pair: TradingPair) -> OrderBook:
        try:
            _ob = connection.fetch_order_book(str(pair))
        except Exception as err:
            raise err
        return self._map_order_book(_ob)

    @staticmethod
    def _map_order_book(ob: Dict) -> OrderBook:
        _bids = [PriceAmount(price=bid[0], amount=bid[1]) for bid in ob['bids']]
        _asks = [PriceAmount(price=bid[0], amount=bid[1]) for bid in ob['asks']]
        return OrderBook(bids=_bids, asks=_asks)

    def get_balance(
            self,
            exchange: Exchange,
            params: Dict = {}
    ) -> Balance:
        self._logger.debug('Reading balance from %s with CCTX', exchange.id)

        _conn = common_cctx.connect(exchange, self._logger)
        try:
            _bal = _conn.fetch_balance(params)
        except Exception as err:
            raise err
        return self._map_balance(_bal)

    def _map_balance(self, bal: Dict) -> Balance:
        _timestamp = self._map_timestamp(bal['timestamp'])
        _free = self._map_by_availability(bal['free'])
        _used = self._map_by_availability(bal['used'])
        _total = self._map_by_availability(bal['total'])
        _currencies = self._map_by_currency(bal)
        _info = bal['info']
        _bal = Balance(
            timestamp=_timestamp,
            free=_free,
            used=_used,
            total=_total,
            currencies=_currencies,
            info=_info,
        )
        self._logger.debug('Read balance: %s', _bal)
        return _bal

    @staticmethod
    def _map_timestamp(timestamp) -> int:
        if timestamp:
            return timestamp
        else:
            return int(time.time() * 1000)

    def _map_by_availability(self, dic: Dict) -> Set[ByAvailability]:
        lst = []
        for sym in dic:
            _by_availability = self._build_by_availability(sym, dic[sym])
            if _by_availability:
                lst.append(_by_availability)
        return lst

    def _build_by_availability(self, sym: str, amount: float):
        try:
            return ByAvailability(currency=Currency(sym), amount=amount)
        except ValueError as err:
            self._logger.warning(err)
            return None

    def _map_by_currency(self, dic: Dict) -> Dict[Currency, ByCurrency]:
        _dic = {}
        for _curr in Currency:
            _dic[_curr.value] = self._map_currency(_curr, dic)
        return _dic

    @staticmethod
    def _map_currency(curr: Currency, dic: Dict) -> Dict[Currency, ByCurrency]:
        try:
            _value = dic[curr.value]
            return ByCurrency(free=_value['free'], used=_value['used'], total=_value['total'])
        except KeyError:
            return ByCurrency(free=0.0, used=0.0, total=0.0)
