import pathlib
from test.elena.domain.services.fake_exchange_manager import \
    FakeExchangeManager
from elena.adapters.bot_manager.local_bot_manager import LocalBotManager
from elena.adapters.config.local_config_reader import LocalConfigReader
from elena.adapters.logger.local_logger import LocalLogger
from elena.domain.model.bot_config import BotConfig
from elena.domain.model.bot_status import BotStatus
from elena.domain.ports.logger import Logger
from elena.domain.ports.strategy_manager import StrategyManager
from elena.domain.services.elena import Elena
from elena.domain.services.generic_bot import GenericBot
from elena.domain.ports.exchange_manager import ExchangeManager


class ExchangeBasicOperationsBot(GenericBot):
    band_length: float
    band_mult: float

    def init(self, manager: StrategyManager, logger: Logger, exchange_manager: ExchangeManager, bot_config: BotConfig, bot_status: BotStatus):  # type: ignore
        super().init(manager, logger, exchange_manager, bot_config, bot_status)

        try:
            self.band_length = bot_config.config["band_length"]
            self.band_mult = bot_config.config["band_mult"]
        except Exception:
            self._logger.error("Error initializing Bot config", exc_info=1)

        # Verify that the exchange is in sandbox mode!!!!
        if not self.exchange.sandbox_mode:
            raise Exception(
                "Exchange is not in sandbox mode, this strategy is ment for testing only!"
            )

    def next(self) -> BotStatus:
        self._logger.info("%s strategy: processing next cycle ...", self.name)

        # is there any free balance to handle?
        balance = self.get_balance()
        if not balance:
            raise Exception("Cannot get balance")

        min_amount = self.limit_min_amount()
        if not min_amount:
            raise Exception("Cannot get min_amount")

        # get candles
        candles = self.read_candles()

        market_sell_order = None
        market_buy_order = None

        while not (market_sell_order or market_buy_order):
            # we can't know if we have balances, so we'll try to buy or sell depending on the balances
            # is there any free balance to handle?
            balance = self.get_balance()
            if not balance:
                raise Exception("Cannot get balance")

            base_symbol = self.pair.base
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
                amount_to_sell = self.amount_to_precision(amount_to_sell)
                if amount_to_sell > min_amount:
                    market_sell_order = self.create_market_sell_order(amount_to_sell)
                else:
                    market_sell_order = None

            # is there any free balance to handle?
            balance = self.get_balance()
            if not balance:
                raise Exception("Cannot get balance")

            quote_symbol = self.pair.quote
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

                amount_to_buy = self.amount_to_precision(amount_to_buy)
                if amount_to_buy > min_amount:
                    market_buy_order = self.create_market_buy_order(amount_to_sell)
                else:
                    pass

            if not (market_sell_order or market_buy_order):
                # but we may have all balances locked...
                self._logger.error(
                    "Can't buy nor sell symbol. Maybe all balances are in open orders."
                )
                break

        # TODO:
        #  - correct precisions for exchange self._manager.price_to_precision(self._exchange,
        #           self._bot_config.pair, new_stop_loss)
        #  - create some stop_loss and cancel it

        return self.status


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
