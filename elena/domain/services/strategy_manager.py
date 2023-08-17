import importlib
from typing import List

import pandas as pd

from elena.domain.model.balance import Balance
from elena.domain.model.bot_config import BotConfig
from elena.domain.model.bot_status import BotStatus
from elena.domain.model.exchange import Exchange, ExchangeType
from elena.domain.model.order import OrderType, OrderSide, Order, OrderStatusType
from elena.domain.model.order_book import OrderBook
from elena.domain.model.strategy_config import StrategyConfig
from elena.domain.ports.bot import Bot
from elena.domain.ports.bot_manager import BotManager
from elena.domain.ports.exchange_manager import ExchangeManager
from elena.domain.model.time_frame import TimeFrame
from elena.domain.ports.logger import Logger
from elena.domain.ports.strategy_manager import StrategyManager
from elena.domain.model.trading_pair import TradingPair

class StrategyManagerImpl(StrategyManager):

    def __init__(self,
                 strategy_config: StrategyConfig,
                 logger: Logger,
                 bot_manager: BotManager,
                 exchange_manager: ExchangeManager,
                 exchanges: List[Exchange],
                 ):
        self._config = strategy_config
        self._logger = logger
        self._bot_manager = bot_manager
        self._exchange_manager = exchange_manager
        self._exchanges = exchanges

    def run(self, previous_statuses: List[BotStatus]) -> List[BotStatus]:
        """
        Runs all strategy bots.
        A Bot is an instance of a strategy with a certain configuration
          1. retrieves the bot status of the previous execution with BotManager
          2. read info from market to define orders with ExchangeManager
          3. run the strategy logic to decide what to do (buy, sell, wait ...)
          4. once decided, if any, write orders to an Exchange with OrderManager
        :param previous_statuses: the list of all bot statuses from previous execution
        :return: the updated statuses list of all bot with any update in the current cycle
        """
        _previous_statuses_dic = {_status.bot_id: _status for _status in previous_statuses}
        _updated_statuses = []
        for _bot_config in self._config.bots:
            self._logger.info(f'Running bot %s: %s', _bot_config.id, _bot_config.name)
            if _bot_config.id in _previous_statuses_dic:
                _status = _previous_statuses_dic[_bot_config.id]
            else:
                _status = BotStatus(bot_id=_bot_config.id, active_orders=[], archived_orders=[], active_trades=[], closed_trades=[])

            _updated_status = self._run_bot(_status, _bot_config)
            _updated_statuses.append(_updated_status)
        return _updated_statuses

    def _run_bot(self, status: BotStatus, bot_config: BotConfig) -> BotStatus:

        _bot = self._get_bot_instance(bot_config)
        _exchange = self.get_exchange(bot_config.exchange_id)
        updated_order_status = self._update_orders_status(_exchange,status, bot_config)
        status = _bot.next(status)

        # _exchange = self._get_exchange(bot_config.exchange_id)
        # TODO: always send time frame... add in config
        # _candles = self._exchange_manager.read_candles(_exchange, bot_config.pair)
        # TODO: _order_book is only necessary if we are going to put an order
        # _order_book = self._exchange_manager.read_order_book(_exchange, bot_config.pair)
        # TODO: _balance is only necessary if we are going to put an order
        # _balance = self._exchange_manager.get_balance(_exchange)
        # TODO:
        # - we should read the order status of our orders (the bot orders).
        # - store the orders on completed trade if some are closed (raise event?)
        # - call an abstract method next()? that is implemented on child class
        # - how do we inject/instantiate that class from a .yaml...
        # - do we need a "bt.init()" on the derivative class? => maybe not.
        # - how do we get the new orders?
        # - since time frame is in the config we can run the bots/run next only when the last execution - now()
        #    is greater than timeframe
        # - take profit? or freeze a part even reinvesting? =>> No, that's on the Strategy code by the user.
        # - move cash between bots?

        # TODO self._bot_manager.run() ?
        # - save any status

        return status

    def _get_bot_instance(self, bot_config: BotConfig) -> Bot:
        _class_parts = self._config.strategy_class.split(".")
        _class_name = _class_parts[-1]
        _module_path = ".".join(_class_parts[0:-1])
        _module = importlib.import_module(_module_path)
        _class = getattr(_module, _class_name)
        _bot = _class()
        _bot.init(manager=self, logger=self._logger, bot_config=bot_config)
        return _bot

    def get_exchange(self, exchange_id: ExchangeType) -> Exchange:
        for exchange in self._exchanges:
            if exchange.id == exchange_id.value:
                return exchange


    def _cancel_order(self, exchange: Exchange, bot_config: BotConfig, order_id: str) -> Order:
        _order = self._exchange_manager.cancel_order(
            exchange=exchange,
            bot_config=bot_config,
            order_id=order_id
        )
        self._logger.info('Canceled order: %s', id)
        return _order

    def buy(self):
        self._logger.error('buy is not implemented')

    def sell(self):
        self._logger.error('sell is not implemented')

    def stop_loss_market(self, exchange: Exchange, bot_config: BotConfig, amount: float, stop_price: float) -> Order:
        # https://docs.ccxt.com/#/README?id=stop-loss-orders
        # sl = exchange.create_order(symbol, 'market', 'sell', amount, None, {'stopPrice': stopLossPrice})

        params = {'stopPrice': stop_price}

        _order = self._exchange_manager.place_order(
            exchange=exchange,
            bot_config=bot_config,
            order_type=OrderType.market,
            side=OrderSide.sell,
            amount=amount,
            params=params
        )
        self._logger.info('Placed market stop loss: %s', _order)

        return _order

    def get_balance(self, exchange: Exchange) -> Balance:
        return self._exchange_manager.get_balance(exchange)

    def read_candles(self, exchange: Exchange, pair: TradingPair, time_frame: TimeFrame = TimeFrame.min_1) -> pd.DataFrame:
        return self._exchange_manager.read_candles(exchange,pair,time_frame )

    def get_order_book(self) -> OrderBook:
        ...

    def _update_orders_status(self, exchange: Exchange, status: BotStatus, bot_config: BotConfig) -> List[Order]:
        # orders
        updated_orders = List[Order]
        for order in status.active_orders:
            # update status
            updated_order = self._exchange_manager.fetch_order(exchange, bot_config, order.id)
            if order.status == OrderStatusType.closed:
                # notify
                # updates trades
                # move to archived
                pass
            else:
                updated_orders.append(updated_order)

        return updated_orders
