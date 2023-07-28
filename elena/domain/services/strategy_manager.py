from typing import List

from elena.domain.model.bot_config import BotConfig
from elena.domain.model.bot_status import BotStatus
from elena.domain.model.exchange import Exchange, ExchangeType
from elena.domain.model.order import OrderType, OrderSide, Order
from elena.domain.model.order_book import OrderBook
from elena.domain.model.strategy_config import StrategyConfig
from elena.domain.ports.bot_manager import BotManager
from elena.domain.ports.exchange_manager import ExchangeManager
from elena.domain.ports.logger import Logger
from elena.domain.ports.strategy_manager import StrategyManager

import pandas as pd


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
        Runs all strategy bots. A Bot is an instance of a strategy with a certain configuration
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
            if _bot_config.id in _previous_statuses_dic:
                _status = _previous_statuses_dic[_bot_config.id]
            else:
                _status = BotStatus(bot_id=_bot_config.id, orders=[])
            _updated_status = self._run_bot(_status, _bot_config)
            _updated_statuses.append(_updated_status)
        return _updated_statuses

    def _run_bot(self, status: BotStatus, bot_config: BotConfig) -> BotStatus:

        # TODO Instantiate bot class with importlib https://docs.python.org/3/library/importlib.html
        _strategy_instance = self._load_strategy_from_class_path()

        status = _bot.next(status, bot_config)

        # _exchange = self._get_exchange(bot_config.exchange_id)
        #TODO: always send time frame... add in config
        # _candles = self._exchange_manager.read_candles(_exchange, bot_config.pair)
        #TODO: _order_book is only necesary if we are going to put an order
        # _order_book = self._exchange_manager.read_order_book(_exchange, bot_config.pair)
        #TODO: _balance is only necesary if we are going to put an order
        # _balance = self._exchange_manager.get_balance(_exchange)
        #TODO:
        # - we should read the order status of our orders (the bot's orders).
        # - store the orders on completed trade if some are closed (raise event?)
        # - call an abstract method next()? that is implemented on child class
        # - how do we inject/instantiate that class from a .yaml...
        # - do we need a "bt.init()" on the derivative class? => maybe not.
        # - how do we get the new orders?
        # - since time frame is in the config we can run the bots/run next only when the last execution - now()
        #    is greater than timeframe
        # - take profit? or freeze a part even revinsting? =>> No, that's on th Strategy code by the user.
        # - move cash between bots?


        # TODO self._bot_manager.run() ?
        # - save any status



        return status

    def _get_exchange(self, exchange_id: ExchangeType) -> Exchange:
        for exchange in self._exchanges:
            if exchange.id == exchange_id.value:
                return exchange

    def _place_order(self, exchange: Exchange, bot_config: BotConfig) -> Order:
        _order = self._exchange_manager.place_order(
            exchange=exchange,
            bot_config=bot_config,
            type=OrderType.limit,
            side=OrderSide.buy,
            amount=0.001,
            price=10_000
        )
        self._logger.info('Placed order: %s', _order)
        return _order

    def _cancel_order(self, exchange: Exchange, bot_config: BotConfig, id: str) -> Order:
        _order = self._exchange_manager.cancel_order(
            exchange=exchange,
            bot_config=bot_config,
            id=id
        )
        self._logger.info('Canceled order: %s', id)
        return _order

    def buy(self):
        ...

    def sell(self):
        ...

    def stop_loss(self):
        ...

    def get_candles(self) -> pd.DataFrame:
        pass

    def get_order_book(self) -> OrderBook:
        pass

    def get_orders(self) -> List[Order]:
        ...
