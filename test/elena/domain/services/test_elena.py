import pathlib
from os import path
from test.elena.domain.services.fake_exchange_manager import \
    FakeExchangeManager

from elena.adapters.bot_manager.local_bot_manager import LocalBotManager
from elena.adapters.config.local_config_reader import LocalConfigReader
from elena.domain.model.bot_config import BotConfig
from elena.domain.model.bot_status import BotStatus
from elena.domain.ports.exchange_manager import ExchangeManager
from elena.domain.ports.logger import Logger
from elena.domain.ports.metrics_manager import MetricsManager
from elena.domain.ports.notifications_manager import NotificationsManager
from elena.domain.ports.strategy_manager import StrategyManager
from elena.domain.services.elena import Elena
from elena.domain.services.generic_bot import GenericBot
from elena.shared.dynamic_loading import get_instance


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

    def _orders_trades_status(self):
        return len(self.status.active_orders), len(self.status.archived_orders), len(self.status.active_trades), len(
            self.status.closed_trades)

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

        active_orders_before_order, archived_orders_before_order, active_trades_before_order, closed_trades_before_order = self._orders_trades_status()

        market_buy_order = self.create_market_buy_order(precision_to_buy)

        if not market_buy_order:
            raise Exception("Buy test failed")

        # TODO: wait order status without recording

        # Check orders & trades
        active_orders_after_order, archived_orders_after_order, active_trades_after_order, closed_trades_after_order = self._orders_trades_status()

        assert active_orders_before_order == active_orders_after_order
        assert archived_orders_after_order == (archived_orders_before_order + 1)
        assert active_trades_after_order == (active_trades_before_order + 1)
        assert closed_trades_before_order == closed_trades_after_order
        # TODO check: order data in archived_orders and trades

        # 3 - STOP LOSS Create
        active_orders_before_order, archived_orders_before_order, active_trades_before_order, closed_trades_before_order = self._orders_trades_status()
        amount_for_stop_loss = market_buy_order.amount
        stop_loss_stop_price = candles["Close"][-1:].iloc[0] * 0.8  # last close - 20%
        stop_loss_price = stop_loss_stop_price * 0.95  # stop_price - 5%
        stop_loss_order = self.stop_loss(amount_for_stop_loss, stop_loss_stop_price, stop_loss_price)
        if not stop_loss_order:
            raise Exception("Stop loss creation failed.")
        # TODO: wait order status without recording

        # Check orders & trades
        active_orders_after_order, archived_orders_after_order, active_trades_after_order, closed_trades_after_order = self._orders_trades_status()
        assert active_orders_after_order == (active_orders_before_order + 1)
        assert archived_orders_after_order == archived_orders_before_order
        assert active_trades_after_order == active_trades_before_order
        assert closed_trades_before_order == closed_trades_after_order

        # 4 - STOP LOSS Cancel
        active_orders_before_order, archived_orders_before_order, active_trades_before_order, closed_trades_before_order = self._orders_trades_status()

        canceled_order = self.cancel_order(stop_loss_order.id)
        if not canceled_order:
            raise Exception("Stop loss cancel failed.")
        # TODO: wait order status without recording

        # Check orders & trades
        active_orders_after_order, archived_orders_after_order, active_trades_after_order, closed_trades_after_order = self._orders_trades_status()
        assert active_orders_after_order == active_orders_before_order - 1
        assert archived_orders_after_order == archived_orders_before_order + 1
        assert active_trades_after_order == active_trades_before_order
        assert closed_trades_before_order == closed_trades_after_order

        # 5 - SELL Market
        active_orders_before_order, archived_orders_before_order, active_trades_before_order, closed_trades_before_order = self._orders_trades_status()
        amount_to_sell = market_buy_order.amount
        market_sell_order = self.create_market_sell_order(amount_to_sell)

        if not market_sell_order:
            raise Exception("Sell test failed")
        # TODO: wait order status without recording

        # Check orders & trades
        active_orders_after_order, archived_orders_after_order, active_trades_after_order, closed_trades_after_order = self._orders_trades_status()
        assert active_orders_after_order == active_orders_before_order - 1
        assert archived_orders_after_order == archived_orders_before_order + 1
        assert active_trades_after_order == active_trades_before_order - 1
        assert closed_trades_before_order == closed_trades_after_order + 1

        return self.status


def test_elena():
    test_home_dir = path.join(pathlib.Path(__file__).parent, "test_home")
    config = LocalConfigReader(test_home_dir).config

    logger = get_instance(config["Logger"]["class"])
    logger.init(config)

    metrics_manager = get_instance(config["MetricsManager"]["class"])
    metrics_manager.init(config, logger)

    notifications_manager = get_instance(config["NotificationsManager"]["class"])
    notifications_manager.init(config, logger)

    bot_manager = LocalBotManager(config, logger, metrics_manager, notifications_manager)
    exchange_manager = FakeExchangeManager(config, logger)

    sut = Elena(
        config=config,
        logger=logger,
        metrics_manager=metrics_manager,
        notifications_manager=notifications_manager,
        bot_manager=bot_manager,
        exchange_manager=exchange_manager,
    )

    sut.run()
