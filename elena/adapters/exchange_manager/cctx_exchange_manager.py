import time
from typing import Dict, List, Optional, Any

import ccxt
import pandas as pd

from elena.domain.model.balance import Balance, ByAvailability, ByCurrency
from elena.domain.model.bot_config import BotConfig
from elena.domain.model.exchange import Exchange, ExchangeType
from elena.domain.model.order import Order, OrderType, OrderSide, OrderStatusType, Fee
from elena.domain.model.order_book import OrderBook, PriceAmount
from elena.domain.model.time_frame import TimeFrame
from elena.domain.model.trading_pair import TradingPair
from elena.domain.ports.exchange_manager import ExchangeManager
from elena.domain.ports.logger import Logger


class CctxExchangeManager(ExchangeManager):
    _connect_mapper = {
        ExchangeType.bitget: ccxt.bitget,
        ExchangeType.kucoin: ccxt.kucoin,
        ExchangeType.binance: ccxt.binance
        # TODO [Pere] auto add others?
    }

    def __init__(self, config: Dict, logger: Logger):
        self._config = config['CctxExchangeManager']
        self._logger = logger

    def _connect(self, exchange: Exchange):
        self._logger.debug('Connecting to %s ...', exchange.id.value)
        _conn = self._connect_mapper[exchange.id]({
            'apiKey': exchange.api_key,
            'password': exchange.password,
            'secret': exchange.secret,
        })
        _conn.set_sandbox_mode(exchange.sandbox_mode)
        self._logger.info('Connected to %s at %s', exchange.id.value, _conn.urls['api']['public'])
        return _conn

    def read_candles(
            self,
            exchange: Exchange,
            pair: TradingPair,
            time_frame: TimeFrame = TimeFrame.min_1
    ) -> pd.DataFrame:
        self._logger.debug('Reading exchange candles from %s with CCTX for pair %s ...', exchange.id, pair)
        _conn = self._connect(exchange)
        _candles = self._fetch_candles(_conn, pair, time_frame)
        self._logger.info('Read %d %s candles from %s', _candles.shape[0], pair, exchange.id.value)
        return _candles

    _columns = ['Open time', 'Open', 'High', 'Low', 'Close', 'Volume']

    def _fetch_candles(self, connection, pair: TradingPair, time_frame: TimeFrame) -> pd.DataFrame:
        candles_list = self._fetch_candles_with_retry(connection, pair, time_frame)
        candles_df = pd.DataFrame(candles_list)
        if candles_df.shape == (0, 0):
            return pd.DataFrame(columns=self._columns)
        candles_df.columns = self._columns
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
                # TODO: I'm not sure fetch_ohlcv_limit should be at CctxExchangeManager, a bot may requiere more data points and others not. May be it can be overwritten.
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

        _conn = self._connect(exchange)
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
            exchange: Exchange
    ) -> Balance:
        self._logger.debug('Reading balance from %s with CCTX', exchange.id)

        _conn = self._connect(exchange)
        try:
            _bal = _conn.fetch_balance()
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
        self._logger.info('Read balance: %s', _bal)
        return _bal

    @staticmethod
    def _map_timestamp(timestamp) -> int:
        if timestamp:
            return timestamp
        else:
            return int(time.time() * 1000)

    def _map_by_availability(self, dic: Dict) -> List[ByAvailability]:
        lst = []
        for sym in dic:
            _by_availability = self._build_by_availability(sym, dic[sym])
            if _by_availability:
                lst.append(_by_availability)
        return lst

    def _build_by_availability(self, sym: str, amount: float):
        try:
            return ByAvailability(currency=sym, amount=amount)
        except ValueError as err:
            self._logger.warning(err)
            return None

    _exclude = ['info', 'timestamp', 'datetime', 'free', 'used', 'total']

    def _map_by_currency(self, dic: Dict) -> Dict[str, ByCurrency]:
        _dic = {}
        for _key in dic:
            if _key in self._exclude:
                continue
            _val = self._map_currency(_key, dic)
            if _val:
                _dic[_key] = _val
        return _dic

    @staticmethod
    def _map_currency(curr: str, dic: Dict) -> Optional[ByCurrency]:
        try:
            _value = dic[curr]
            return ByCurrency(free=_value['free'], used=_value['used'], total=_value['total'])
        except KeyError:
            return None

    def place_order(
            self,
            exchange: Exchange,
            bot_config: BotConfig,
            type: OrderType,
            side: OrderSide,
            amount: float,
            price: Optional[float] = None
    ) -> Order:
        _conn = self._connect(exchange)
        _order = _conn.create_order(
            symbol=str(bot_config.pair),
            type=type.value,
            side=side.value,
            amount=amount,
            price=price
        )
        result = self._map_order(exchange, bot_config, bot_config.pair, _order)
        return result

    def _map_order(self, exchange: Exchange, bot_config: BotConfig, pair: TradingPair, order) -> Order:
        return Order(
            id=order['id'],
            exchange_id=exchange.id,
            bot_id=bot_config.id,
            strategy_id=bot_config.strategy_id,
            pair=pair,
            timestamp=order['timestamp'],
            type=OrderType(order['type']),
            side=OrderSide(order['side']),
            price=order['price'],
            amount=order['amount'],
            cost=order['cost'],
            average=order['average'],
            filled=order['filled'],
            remaining=order['remaining'],
            status=self._map_status(order['status']),
            fee=self._map_fee(order['fee']),
        )

    @staticmethod
    def _map_status(status) -> Optional[OrderStatusType]:
        if status:
            return OrderStatusType(status)
        else:
            return None

    def _map_fee(self, fee) -> Optional[Fee]:
        if fee:
            _curr = self._nvl(fee, 'currency', None)
            if _curr:
                return Fee(
                    currency=_curr,
                    cost=self._nvl(fee, 'cost', 0.0),
                    rate=self._nvl(fee, 'rate', 0.0),
                )
        return None

    @staticmethod
    def _nvl(dic: Dict, key: str, default_value: Any) -> Any:
        try:
            return dic[key]
        except KeyError:
            return default_value

    def cancel_order(
            self,
            exchange: Exchange,
            bot_config: BotConfig,
            id: str
    ):
        _conn = self._connect(exchange)
        _conn.cancel_order(
            id=id,
            symbol=str(bot_config.pair)
        )

    def fetch_order(
            self,
            exchange: Exchange,
            bot_config: BotConfig,
            id: str
    ) -> Order:
        _conn = self._connect(exchange)
        _order = _conn.fetch_order(
            id=id,
            symbol=str(bot_config.pair)
        )
        result = self._map_order(exchange, bot_config, bot_config.pair, _order)
        return result
