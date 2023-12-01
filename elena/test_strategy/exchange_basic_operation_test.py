from logging import Logger

from elena.domain.model.bot_config import BotConfig
from elena.domain.model.bot_status import BotStatus
from elena.domain.model.time_frame import TimeFrame
from elena.domain.model.exchange import Exchange
from elena.domain.ports.bot import Bot
from elena.domain.ports.strategy_manager import StrategyManager


class ExchangeBasicOperationsTest(Bot):
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
        self._exchange = self._manager.get_exchange(self._config.exchange_id)

        try:
            self.band_length = bot_config.config['band_length']
            self.band_mult = bot_config.config['band_mult']
        except Exception as err:
            logger.error('Error initializing Bot config')
            logger.error(f"Unexpected {err=}, {type(err)=}")

    def next(self, status: BotStatus) -> BotStatus:
        self._logger.info("%s strategy: processing next cycle ...", self._name)

        # Verify that the exchange is in sandbox mode!!!!
        if not self._exchange.sandbox_mode:
            raise Exception("Exchange is not in sandbox mode, this strategy is ment for testing only!")

        # is there any free balance to handle?
        balance = self._manager.get_balance(self._exchange)

        base_symbol = self._config.pair.base
        base_total = balance.currencies[base_symbol].total
        base_free = balance.currencies[base_symbol].free

        quote_symbol = self._config.pair.quote
        quote_total = balance.currencies[quote_symbol].total
        quote_free = balance.currencies[quote_symbol].free

        # get min amount
        min_amount = self._manager.limit_min_amount(self._exchange, self._config.pair)

        # get candles
        candles = self._manager.read_candles(self._exchange, self._config.pair, TimeFrame.day_1)

        # correct precisions for exchange
        # new_stop_loss = self._manager.price_to_precision(self._exchange, self._bot_config.pair, new_stop_loss)
        # price = self._manager.price_to_precision(self._exchange, self._bot_config.pair, price)
        # new_trade_size = self._manager.amount_to_precision(self._exchange, self._bot_config.pair, new_trade_size)

        # if we have base_symbol_free => market order sell
        # take that money and buy it again with some calc over the candles
        # can we know the open orders? if can => cancel any and create some stop_loss

        return status
