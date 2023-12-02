import pathlib
from logging import Logger
from test.elena.domain.services.fake_exchange_manager import \
    FakeExchangeManager

from elena.adapters.bot_manager.local_bot_manager import LocalBotManager
from elena.adapters.config.local_config_reader import LocalConfigReader
from elena.adapters.logger.local_logger import LocalLogger
from elena.domain.model.bot_config import BotConfig
from elena.domain.model.bot_status import BotStatus
from elena.domain.model.exchange import Exchange
from elena.domain.model.time_frame import TimeFrame
from elena.domain.ports.bot import Bot
from elena.domain.ports.strategy_manager import StrategyManager
from elena.domain.services.elena import Elena


class ExchangeBasicOperationsBot(Bot):
    _manager: StrategyManager
    _logger: Logger
    _config: BotConfig
    _exchange: Exchange
    _name: str
    band_length: float
    band_mult: float

    def init(self, manager: StrategyManager, logger: Logger, bot_config: BotConfig):  # type: ignore
        self._manager = manager
        self._logger = logger
        self._name = self.__class__.__name__
        self._config = bot_config

        exchange = self._manager.get_exchange(self._config.exchange_id)
        if not exchange:
            raise Exception(f"Cannot get Exchange from {self._config.exchange_id} ID")
        self._exchange = exchange

        try:
            self.band_length = bot_config.config["band_length"]
            self.band_mult = bot_config.config["band_mult"]
        except Exception as err:
            logger.error("Error initializing Bot config")
            logger.error(f"Unexpected {err=}, {type(err)=}")

    def next(self, status: BotStatus) -> BotStatus:
        self._logger.info("%s strategy: processing next cycle ...", self._name)

        # Verify that the exchange is in sandbox mode!!!!
        if not self._exchange.sandbox_mode:
            raise Exception(
                "Exchange is not in sandbox mode, this strategy is ment for testing only!"
            )

        # get min amount
        min_amount = self._manager.limit_min_amount(self._exchange, self._config.pair)

        # get candles
        candles = self._manager.read_candles(self._exchange, self._config.pair, TimeFrame.day_1)

        market_sell_order = None
        market_buy_order = None

        while not (market_sell_order or market_buy_order):
            # we can't know if we have balances, so we'll try to buy or sell depending on the balances
            # is there any free balance to handle?
            balance = self._manager.get_balance(self._exchange)

            base_symbol = self._config.pair.base
            base_total = balance.currencies[base_symbol].total
            base_free = balance.currencies[base_symbol].free

            # if we have base_symbol_free => market order sell
            # BTC/USDT: if we have BTC we sell it for USDT
            if base_free > 0:
                if market_buy_order:
                    # if we bought before we sell that amount
                    amount_to_sell = market_buy_order.amount
                else:
                    amount_to_sell = base_free / 2
                amount_to_sell = self._manager.amount_to_precision(self._exchange, self._config.pair, amount_to_sell)
                if amount_to_sell > min_amount:
                    market_sell_order = self._manager.sell_market(self._exchange, self._config, amount_to_sell)
                else:
                    market_sell_order = None

            # is there any free balance to handle?
            balance = self._manager.get_balance(self._exchange)

            quote_symbol = self._config.pair.quote
            quote_total = balance.currencies[quote_symbol].total
            quote_free = balance.currencies[quote_symbol].free

            # if we have quote_free => market order buy
            # BTC/USDT: if we have USDT we buy USDT

            if quote_free > 0:
                # if we could sell some BTC we buy the same again
                if market_sell_order:
                    amount_to_buy = market_sell_order.amount
                else:
                    # if we couldn't sell we use the free USDT to buy
                    # TODO: Implement exchange.fetch_ticker(symbol) or OrderBook to have a better price reference.
                    yesterday_close_price = float(candles["Close"][-2:-1].iloc[0])
                    amount_to_spend = quote_free / 2
                    amount_to_buy = amount_to_spend / yesterday_close_price

                amount_to_buy = self._manager.amount_to_precision(self._exchange, self._config.pair, amount_to_buy)
                if amount_to_buy > min_amount:
                    market_buy_order = self._manager.buy_market(self._exchange, self._config, amount_to_buy)
                else:
                    pass

            if not (market_sell_order or market_buy_order):
                # but we may have all balances locked...
                self._logger.error("Can't buy nor sell symbol. Maybe all balances are in open orders.")
                break

        # TODO:
        #  - correct precisions for exchange self._manager.price_to_precision(self._exchange,
        #           self._bot_config.pair, new_stop_loss)
        #  - create some stop_loss and cancel it

        return status


def test_elena():
    home = pathlib.Path(__file__).parent.parent.parent.__str__()
    config = LocalConfigReader(home).config
    logger = LocalLogger(config)
    bot_manager = LocalBotManager(config, logger)
    exchange_manager = FakeExchangeManager(config, logger)

    sut = Elena(
        config=config,
        logger=logger,
        bot_manager=bot_manager,
        exchange_manager=exchange_manager,
    )

    sut.run()
