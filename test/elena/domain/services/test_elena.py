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


class ExchangeBasicOperationsBot(GenericBot):
    band_length: float
    band_mult: float

    def init(self, manager: StrategyManager, logger: Logger, bot_config: BotConfig):  # type: ignore
        super().init(manager, logger, bot_config)

        try:
            self.band_length = bot_config.config["band_length"]
            self.band_mult = bot_config.config["band_mult"]
        except Exception as err:
            self._logger.error(f"Error initializing Bot config: {err}", error=err)

        # Verify that the exchange is in sandbox mode!!!!
        if not self.exchange.sandbox_mode:
            raise Exception(
                "Exchange is not in sandbox mode, this strategy is ment for testing only!"
            )

    def next(self, status: BotStatus) -> BotStatus:
        self._logger.info("%s strategy: processing next cycle ...", self.name)

        # is there any free balance to handle?
        balance = self.get_balance()
        if not balance:
            raise Exception("Cannot get balance")

        base_symbol = self.pair.base
        base_total = balance.currencies[base_symbol].total
        base_free = balance.currencies[base_symbol].free

        quote_symbol = self.pair.quote
        quote_total = balance.currencies[quote_symbol].total
        quote_free = balance.currencies[quote_symbol].free

        # get min amount
        min_amount = self.limit_min_amount()

        # get candles
        candles = self.read_candles(page_size=100)

        # correct precisions for exchange
        # new_stop_loss = self._manager.price_to_precision(self._exchange, self._bot_config.pair, new_stop_loss)
        # price = self._manager.price_to_precision(self._exchange, self._bot_config.pair, price)
        # new_trade_size = self._manager.amount_to_precision(self._exchange, self._bot_config.pair, new_trade_size)

        # if we have base_symbol_free => market order sell
        # take that money and buy it again with some calc over the candles
        # can we know the open orders? if can => cancel any and create some stop_loss

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
