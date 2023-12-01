import time
from typing import Any, Dict, List, Optional

import ccxt
import pandas as pd

from elena.domain.model.balance import Balance, ByAvailability, ByCurrency
from elena.domain.model.bot_config import BotConfig
from elena.domain.model.exchange import Exchange, ExchangeType
from elena.domain.model.order import (Fee, Order, OrderSide, OrderStatusType,
                                      OrderType)
from elena.domain.model.order_book import OrderBook, PriceAmount
from elena.domain.model.time_frame import TimeFrame
from elena.domain.model.trading_pair import TradingPair
from elena.domain.ports.exchange_manager import ExchangeManager
from elena.domain.ports.logger import Logger


class CctxExchangeManager(ExchangeManager):
    _connect_mapper = {
        ExchangeType.ace: ccxt.ace,
        ExchangeType.alpaca: ccxt.alpaca,
        ExchangeType.ascendex: ccxt.ascendex,
        ExchangeType.bequant: ccxt.bequant,
        ExchangeType.bigone: ccxt.bigone,
        ExchangeType.binance: ccxt.binance,
        ExchangeType.binancecoinm: ccxt.binancecoinm,
        ExchangeType.binanceus: ccxt.binanceus,
        ExchangeType.binanceusdm: ccxt.binanceusdm,
        ExchangeType.bingx: ccxt.bingx,
        ExchangeType.bit2c: ccxt.bit2c,
        ExchangeType.bitbank: ccxt.bitbank,
        ExchangeType.bitbay: ccxt.bitbay,
        ExchangeType.bitbns: ccxt.bitbns,
        ExchangeType.bitcoincom: ccxt.bitcoincom,
        ExchangeType.bitfinex: ccxt.bitfinex,
        ExchangeType.bitfinex2: ccxt.bitfinex2,
        ExchangeType.bitflyer: ccxt.bitflyer,
        ExchangeType.bitforex: ccxt.bitforex,
        ExchangeType.bitget: ccxt.bitget,
        ExchangeType.bithumb: ccxt.bithumb,
        ExchangeType.bitmart: ccxt.bitmart,
        ExchangeType.bitmex: ccxt.bitmex,
        ExchangeType.bitopro: ccxt.bitopro,
        ExchangeType.bitpanda: ccxt.bitpanda,
        ExchangeType.bitrue: ccxt.bitrue,
        ExchangeType.bitso: ccxt.bitso,
        ExchangeType.bitstamp: ccxt.bitstamp,
        ExchangeType.bitstamp1: ccxt.bitstamp1,
        ExchangeType.bittrex: ccxt.bittrex,
        ExchangeType.bitvavo: ccxt.bitvavo,
        ExchangeType.bl3p: ccxt.bl3p,
        ExchangeType.blockchaincom: ccxt.blockchaincom,
        ExchangeType.btcalpha: ccxt.btcalpha,
        ExchangeType.btcbox: ccxt.btcbox,
        ExchangeType.btcmarkets: ccxt.btcmarkets,
        ExchangeType.btctradeua: ccxt.btctradeua,
        ExchangeType.btcturk: ccxt.btcturk,
        ExchangeType.bybit: ccxt.bybit,
        ExchangeType.cex: ccxt.cex,
        ExchangeType.coinbase: ccxt.coinbase,
        ExchangeType.coinbaseprime: ccxt.coinbaseprime,
        ExchangeType.coinbasepro: ccxt.coinbasepro,
        ExchangeType.coincheck: ccxt.coincheck,
        ExchangeType.coinex: ccxt.coinex,
        ExchangeType.coinfalcon: ccxt.coinfalcon,
        ExchangeType.coinmate: ccxt.coinmate,
        ExchangeType.coinone: ccxt.coinone,
        ExchangeType.coinsph: ccxt.coinsph,
        ExchangeType.coinspot: ccxt.coinspot,
        ExchangeType.cryptocom: ccxt.cryptocom,
        ExchangeType.currencycom: ccxt.currencycom,
        ExchangeType.delta: ccxt.delta,
        ExchangeType.deribit: ccxt.deribit,
        ExchangeType.digifinex: ccxt.digifinex,
        ExchangeType.exmo: ccxt.exmo,
        ExchangeType.fmfwio: ccxt.fmfwio,
        ExchangeType.gate: ccxt.gate,
        ExchangeType.gateio: ccxt.gateio,
        ExchangeType.gemini: ccxt.gemini,
        ExchangeType.hitbtc: ccxt.hitbtc,
        ExchangeType.hitbtc3: ccxt.hitbtc3,
        ExchangeType.hollaex: ccxt.hollaex,
        ExchangeType.huobi: ccxt.huobi,
        ExchangeType.huobijp: ccxt.huobijp,
        ExchangeType.huobipro: ccxt.huobipro,
        ExchangeType.idex: ccxt.idex,
        ExchangeType.independentreserve: ccxt.independentreserve,
        ExchangeType.indodax: ccxt.indodax,
        ExchangeType.kraken: ccxt.kraken,
        ExchangeType.krakenfutures: ccxt.krakenfutures,
        ExchangeType.kucoin: ccxt.kucoin,
        ExchangeType.kucoinfutures: ccxt.kucoinfutures,
        ExchangeType.kuna: ccxt.kuna,
        ExchangeType.latoken: ccxt.latoken,
        ExchangeType.lbank: ccxt.lbank,
        ExchangeType.lbank2: ccxt.lbank2,
        ExchangeType.luno: ccxt.luno,
        ExchangeType.lykke: ccxt.lykke,
        ExchangeType.mercado: ccxt.mercado,
        ExchangeType.mexc: ccxt.mexc,
        ExchangeType.mexc3: ccxt.mexc3,
        ExchangeType.ndax: ccxt.ndax,
        ExchangeType.novadax: ccxt.novadax,
        ExchangeType.oceanex: ccxt.oceanex,
        ExchangeType.okcoin: ccxt.okcoin,
        ExchangeType.okex: ccxt.okex,
        ExchangeType.okex5: ccxt.okex5,
        ExchangeType.okx: ccxt.okx,
        ExchangeType.paymium: ccxt.paymium,
        ExchangeType.phemex: ccxt.phemex,
        ExchangeType.poloniex: ccxt.poloniex,
        ExchangeType.poloniexfutures: ccxt.poloniexfutures,
        ExchangeType.probit: ccxt.probit,
        ExchangeType.tidex: ccxt.tidex,
        ExchangeType.timex: ccxt.timex,
        ExchangeType.tokocrypto: ccxt.tokocrypto,
        ExchangeType.upbit: ccxt.upbit,
        ExchangeType.wavesexchange: ccxt.wavesexchange,
        ExchangeType.wazirx: ccxt.wazirx,
        ExchangeType.whitebit: ccxt.whitebit,
        ExchangeType.woo: ccxt.woo,
        ExchangeType.yobit: ccxt.yobit,
        ExchangeType.zaif: ccxt.zaif,
        ExchangeType.zonda: ccxt.zonda,
    }
    _candles_columns = ["Open time", "Open", "High", "Low", "Close", "Volume"]

    def __init__(self, config: Dict, logger: Logger):
        self._config = config["CctxExchangeManager"]
        self._logger = logger
        self._conn = None

    def _connect(self, exchange: Exchange):
        if self._conn is None:  # TODO: WARNING one cache for only ONE Exchange
            self._logger.debug("Connecting to %s ...", exchange.id.value)
            conn = self._connect_mapper[exchange.id](
                {
                    "apiKey": exchange.api_key,
                    "password": exchange.password,
                    "secret": exchange.secret,
                }
            )
            conn.set_sandbox_mode(exchange.sandbox_mode)
            self._logger.debug("Loading markets from %s ...", exchange.id.value)
            conn.load_markets()
            self._logger.info(
                "Connected to %s at %s", exchange.id.value, conn.urls["api"]["public"]
            )
            self._conn = conn
        return self._conn

    def read_candles(
        self,
        exchange: Exchange,
        pair: TradingPair,
        time_frame: TimeFrame = TimeFrame.min_1,  # type: ignore
    ) -> pd.DataFrame:
        self._logger.debug(
            "Reading exchange candles from %s with CCTX for pair %s ...",
            exchange.id,
            pair,
        )
        conn = self._connect(exchange)
        candles = self._fetch_candles(conn, pair, time_frame)
        self._logger.info(
            "Read %d %s candles from %s", candles.shape[0], pair, exchange.id.value
        )
        return candles

    def _fetch_candles(
        self, connection, pair: TradingPair, time_frame: TimeFrame
    ) -> pd.DataFrame:
        candles_list = self._fetch_candles_with_retry(connection, pair, time_frame)
        candles_df = pd.DataFrame(candles_list)
        if candles_df.shape == (0, 0):
            return pd.DataFrame(columns=self._candles_columns)
        candles_df.columns = self._candles_columns
        candles_df["Open time"] = pd.to_numeric(
            candles_df["Open time"], downcast="integer"
        )
        candles_df["Open"] = pd.to_numeric(candles_df["Open"], downcast="float")
        candles_df["High"] = pd.to_numeric(candles_df["High"], downcast="float")
        candles_df["Low"] = pd.to_numeric(candles_df["Low"], downcast="float")
        candles_df["Close"] = pd.to_numeric(candles_df["Close"], downcast="float")
        candles_df["Volume"] = pd.to_numeric(candles_df["Volume"], downcast="float")
        candles_df.set_index("Open time")
        return candles_df

    def _fetch_candles_with_retry(
        self, connection, pair: TradingPair, time_frame: TimeFrame
    ) -> List[List]:
        # https://github.com/ccxt/ccxt/issues/10273
        # from https://github.com/ccxt/ccxt/blob/master/examples/py/kucoin-rate-limit.py
        i = 0
        retry = True
        candles = pd.DataFrame()
        while retry:
            try:
                candles = connection.fetch_ohlcv(
                    str(pair), time_frame.value, limit=self._config["fetch_ohlcv_limit"]
                )
                retry = False
            except ccxt.RateLimitExceeded as e:
                self._logger.info(
                    "Retrying connection to exchange, %s: %s", type(e).__name__, e
                )
                connection.sleep(
                    self._config["fetch_ohlcv_limit_retry_every_milliseconds"]
                )
            except Exception as err:
                raise err
            i += 1
        return candles

    def read_order_book(self, exchange: Exchange, pair: TradingPair) -> OrderBook:
        self._logger.debug(
            "Reading exchange order book from %s with CCTX for pair %s ...",
            exchange.id,
            pair,
        )

        conn = self._connect(exchange)
        ob = self._fetch_order_book(conn, pair)
        self._logger.info(
            "Read %d bids and %d asks for %s from %s",
            len(ob.bids),
            len(ob.asks),
            pair,
            exchange.id.value,
        )
        return ob

    def _fetch_order_book(self, connection, pair: TradingPair) -> OrderBook:
        try:
            ob = connection.fetch_order_book(str(pair))
        except Exception as err:
            raise err
        return self._map_order_book(ob)

    @staticmethod
    def _map_order_book(ob: Dict) -> OrderBook:
        bids = [PriceAmount(price=bid[0], amount=bid[1]) for bid in ob["bids"]]
        asks = [PriceAmount(price=bid[0], amount=bid[1]) for bid in ob["asks"]]
        return OrderBook(bids=bids, asks=asks)

    def get_balance(self, exchange: Exchange) -> Balance:
        self._logger.debug("Reading balance from %s with CCTX", exchange.id)

        conn = self._connect(exchange)
        try:
            bal = conn.fetch_balance()
        except Exception as err:
            raise err
        return self._map_balance(bal)

    def _map_balance(self, bal: Dict) -> Balance:
        timestamp = self._map_timestamp(bal["timestamp"])
        free = self._map_by_availability(bal["free"])
        used = self._map_by_availability(bal["used"])
        total = self._map_by_availability(bal["total"])
        currencies = self._map_by_currency(bal)
        info = bal["info"]
        bal = Balance(
            timestamp=timestamp,
            free=free,
            used=used,
            total=total,
            currencies=currencies,
            info=info,
        )
        self._logger.debug("Read balance: %s", bal)
        return bal

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

    _exclude = ["info", "timestamp", "datetime", "free", "used", "total"]

    def _map_by_currency(self, balance: Dict) -> Dict[str, ByCurrency]:
        currencies = {}
        for currency in balance:
            if currency in self._exclude:
                continue
            value = self._map_currency(currency, balance)
            if value:
                currencies[currency] = value
        return currencies

    @staticmethod
    def _map_currency(currency: str, balance: Dict) -> Optional[ByCurrency]:
        try:
            value = balance[currency]
            return ByCurrency(
                free=value["free"], used=value["used"], total=value["total"]
            )
        except KeyError:
            return None

    def place_order(
        self,
        exchange: Exchange,
        bot_config: BotConfig,
        order_type: OrderType,
        side: OrderSide,
        amount: float,
        price: Optional[float] = None,
        params: Optional[Dict] = {},
    ) -> Order:
        conn = self._connect(exchange)
        order = conn.create_order(
            symbol=str(bot_config.pair),
            type=order_type.value,
            side=side.value,
            amount=amount,
            price=price,
            params=params,
        )
        result = self._map_order(exchange, bot_config, bot_config.pair, order)
        return result

    def _map_order(
        self, exchange: Exchange, bot_config: BotConfig, pair: TradingPair, order
    ) -> Order:
        return Order(
            id=order["id"],
            exchange_id=exchange.id,
            bot_id=bot_config.id,
            strategy_id=bot_config.strategy_id,
            pair=pair,
            timestamp=order["timestamp"],
            type=OrderType(order["type"]),
            side=OrderSide(order["side"]),
            price=order["price"],
            amount=order["amount"],
            cost=order["cost"],
            average=order["average"],
            filled=order["filled"],
            remaining=order["remaining"],
            trigger_price=order["triggerPrice"],
            stop_price=order["stopPrice"],
            take_profit_price=order["takeProfitPrice"],
            stop_loss_price=order["stopLossPrice"],
            status=self._map_status(order["status"]),
            fee=self._map_fee(order["fee"]),
        )

    @staticmethod
    def _map_status(status) -> Optional[OrderStatusType]:
        if status:
            return OrderStatusType(status)
        else:
            return None

    def _map_fee(self, fee) -> Optional[Fee]:
        if fee:
            currency = self._nvl(fee, "currency", None)
            if currency:
                return Fee(
                    currency=currency,
                    cost=self._nvl(fee, "cost", 0.0),
                    rate=self._nvl(fee, "rate", 0.0),
                )
        return None

    @staticmethod
    def _nvl(dic: Dict, key: str, default_value: Any) -> Any:
        try:
            return dic[key]
        except KeyError:
            return default_value

    def cancel_order(self, exchange: Exchange, bot_config: BotConfig, order_id: str):
        conn = self._connect(exchange)
        conn.cancel_order(id=order_id, symbol=str(bot_config.pair))

    def fetch_order(
        self, exchange: Exchange, bot_config: BotConfig, order_id: str
    ) -> Order:
        conn = self._connect(exchange)
        order = conn.fetch_order(id=order_id, symbol=str(bot_config.pair))
        result = self._map_order(exchange, bot_config, bot_config.pair, order)
        return result

    def limit_min_amount(self, exchange: Exchange, pair: TradingPair) -> float:

        conn = self._connect(exchange)
        return float(conn.markets[str(pair)]["limits"]["amount"]["min"])

    def amount_to_precision(
        self, exchange: Exchange, pair: TradingPair, amount: float
    ) -> float:
        conn = self._connect(exchange)
        if amount > 0:
            return float(conn.amount_to_precision(str(pair), amount))
        else:
            return 0.0

    def price_to_precision(
        self, exchange: Exchange, pair: TradingPair, price: float
    ) -> float:
        conn = self._connect(exchange)
        if price > 0:
            return float(conn.price_to_precision(str(pair), price))
        else:
            return 0.0
