import pathlib
from os import path

from entrypoint.local.entrypoint import get_elena_instance

from elena.domain.model.bot_config import BotConfig
from elena.domain.model.bot_status import BotStatus
from elena.domain.ports.exchange_manager import ExchangeManager
from elena.domain.ports.logger import Logger
from elena.domain.ports.metrics_manager import MetricsManager
from elena.domain.ports.notifications_manager import NotificationsManager
from elena.domain.ports.strategy_manager import StrategyManager
from elena.domain.services.generic_bot import GenericBot


class ExchangeBasicOperationsBot(GenericBot):
    band_length: float
    band_mult: float

    def init(
        self,
        manager: StrategyManager,
        logger: Logger,
        metrics_manager: MetricsManager,
        notifications_manager: NotificationsManager,
        exchange_manager: ExchangeManager,
        bot_config: BotConfig,
        bot_status: BotStatus,
    ):  # type: ignore
        super().init(
            manager,
            logger,
            metrics_manager,
            notifications_manager,
            exchange_manager,
            bot_config,
            bot_status,
        )

        # without try: if it fails the test fails, and it's OK
        self.band_length = bot_config.config["band_length"]
        self.band_mult = bot_config.config["band_mult"]

        # Verify that the exchange is in sandbox mode!!!!
        if not self.exchange.sandbox_mode:
            raise Exception("Exchange is not in sandbox mode, this strategy is ment for testing only!")

    def next(self) -> BotStatus:
        self._logger.info("%s strategy: processing next cycle ...", self.name)

        # 1 - INFO
        min_amount = self.limit_min_amount()
        if not min_amount:
            raise Exception("Cannot get min_amount")

        candles = self.read_candles()
        if candles.empty:
            raise Exception("Cannot get candles")

        estimated_close_price = self.get_estimated_last_close()
        if not estimated_close_price:
            raise Exception("Cannot get_estimated_last_close")

        balance = self.get_balance()
        if not balance:
            raise Exception("Cannot get balance")

        quote_symbol = self.pair.quote
        quote_free = balance.currencies[quote_symbol].free

        # 2 - BUY Market
        amount_to_spend = quote_free / 2
        amount_to_buy = amount_to_spend / estimated_close_price
        precision_to_buy = self.amount_to_precision(amount_to_buy)
        if not precision_to_buy:
            raise Exception(f"Cannot get precision_to_buy for amount_to_buy {amount_to_buy}")

        if precision_to_buy < min_amount:
            raise Exception("Not enough balance to run the tests. {self.pair.base} = {base_free} / {quote_free}")

        market_buy_order = self.create_market_buy_order(precision_to_buy)

        if not market_buy_order:
            raise Exception("Buy test failed")
        # TODO: check orders & trades

        # 3 - STOP LOSS Create
        amount_for_stop_loss = market_buy_order.amount
        stop_loss_stop_price = candles["Close"][-1:].iloc[0] * 0.8  # last close - 20%
        stop_loss_price = stop_loss_stop_price * 0.95  # stop_price - 5%
        stop_loss_order = self.stop_loss(amount_for_stop_loss, stop_loss_stop_price, stop_loss_price)
        if not stop_loss_order:
            raise Exception("Stop loss creation failed.")
        # TODO: check orders & trades

        # 4 - STOP LOSS Cancel
        canceled_order = self.cancel_order(stop_loss_order.id)
        if not canceled_order:
            raise Exception("Stop loss cancel failed.")
        # TODO: check orders & trades

        # 5 - SELL Market
        amount_to_sell = market_buy_order.amount
        market_sell_order = self.create_market_sell_order(amount_to_sell)

        if not market_sell_order:
            raise Exception("Sell test failed")
        # TODO: check orders & trades

        return self.status


def test_elena():
    sut = get_elena_instance(
        config_manager_class_path="elena.adapters.config.local_config_manager.LocalConfigManager",
        config_manager_url=path.join(pathlib.Path(__file__).parent, "test_home"),
    )
    sut.run()
