import time
from typing import List, Optional

from pydantic import BaseModel, Field

from elena.domain.model.order import Order, OrderSide, OrderStatusType
from elena.domain.model.trade import Trade


class BotBudget(BaseModel):
    # Budget expressed on quote to spend in the strategy.
    set_limit: float = 0.0  # Limit set on the bot configuration.
    current_limit: float = 0.0  # Limit to use now, if profit is taken this number will increase over set_limit.
    used: float = 0.0  # Budget currently used
    pct_reinvest_profit: float = 100.0  # set how much to re-invest en percentage.

    def set(self, budget: float):
        # Every time a set comes with a new value the budget is changed
        # No matter if there are accumulated profit.
        # While the user kept the same budget on the bot configuration
        # the current_limit can use the profit.
        if self.set_limit != budget:
            self.set_limit = budget
            self.current_limit = budget

    def lock(self, locked: float):
        if self.is_budget_limited and self.free > locked:
            # TODO: raise? return false? as it is now the operation is already done...
            pass
        self.used = round(self.used + locked, 8)

    def unlock(self, released: float, rtn: float):
        if self.is_budget_limited and self.used > released:
            # TODO: think!
            pass
        # TODO profit control in budget
        released_without_profit = released - rtn
        self.used = round(self.used - released_without_profit, 8)

        re_usable_profit = rtn
        if self.pct_reinvest_profit != 100.0 and rtn > 0.0:
            re_usable_profit = (rtn * (self.pct_reinvest_profit / 100))

        self.current_limit = round(self.current_limit + re_usable_profit, 8)

    @property
    def free(self) -> float:
        return round(self.current_limit - self.used, 8)

    @property
    def is_budget_limited(self) -> bool:
        return self.set_limit > 0.0

    @property
    def total(self) -> float:
        return round(self.free + self.used, 8)


class BotStatus(BaseModel):
    bot_id: str
    timestamp: int = int(time.time() * 1000)
    active_orders: List[Order]
    archived_orders: List[Order]
    active_trades: List[Trade]
    closed_trades: List[Trade]
    budget: BotBudget

    def _new_trade_by_order(self, order: Order) -> str:
        # All Trades start/"born" here...
        new_trade = Trade(
            exchange_id=order.exchange_id,
            bot_id=self.bot_id,
            strategy_id=order.strategy_id,
            pair=order.pair,
            size=order.amount,
            entry_order_id=order.id,
            entry_price=order.average,
            entry_cost=order.cost,
            entry_time=order.timestamp,
            exit_order_id='0',  # TODO define an OrderId.Null
            exit_price=0.0,
            exit_cost=0.0,
        )
        self.active_trades.append(new_trade)
        return new_trade.id

    @staticmethod
    def _get_trade_precision(f1: float) -> int:
        # https://stackoverflow.com/questions/3018758/determine-precision-and-scale-of-particular-number-in-python
        # TODO: review solution
        str1 = str(f1)
        return len(str1.split(".")[1])

    @staticmethod
    def _calc_update_trade_return_and_duration(trade: Trade) -> float:
        trade.duration = trade.exit_time - trade.entry_time
        trade.profit = trade.exit_cost - trade.entry_cost
        trade.return_pct = (trade.profit / trade.entry_cost) * 100
        return trade.profit

    def _close_individual_trade_on_new_order(self, trade: Trade, order: Order, amount_to_close: float, rtn: float) -> (float, float):
        size_precision = self._get_trade_precision(trade.size)  # done to avoid a call to Exchange to round amount_to_close at retrun
        if trade.size <= round(amount_to_close, size_precision):
            self.active_trades.remove(trade)
            trade.exit_order_id = order.id
            trade.exit_time = order.timestamp
            trade.exit_price = order.average
            trade.exit_cost = order.cost * (trade.size / order.amount)
            rtn = rtn + self._calc_update_trade_return_and_duration(trade)
            self.closed_trades.append(trade)
            return amount_to_close - trade.size, rtn
        else:
            # self._logger.error(f"Amount to close is insufficient for trade id:{trade.id} size: {trade.size} on order {order.id} size: {order.amount} with pending to close {amount_to_close}")
            return amount_to_close, rtn

    def _close_trades_on_new_updated_order(self, order: Order) -> float:
        amount_to_close = order.amount
        rtn = 0.0
        # check trades with an exit order id
        for trade in self.active_trades[:]:
            if trade.exit_order_id == order.id and amount_to_close > 0:
                amount_to_close, rtn = self._close_individual_trade_on_new_order(trade, order, amount_to_close, rtn)

        # check trades without an exit order id
        if amount_to_close > 0:
            for trade in self.active_trades[:]:
                if trade.exit_order_id == '0' and amount_to_close > 0:  # TODO define an OrderId.Null
                    amount_to_close, rtn = self._close_individual_trade_on_new_order(trade, order, amount_to_close, rtn)

        # close trade even with a different order_id
        if amount_to_close > 0:
            # self._logger.warning("The order size is bigger than the trades with an explicit order_id or a blank order_id")
            for trade in self.active_trades[:]:
                if amount_to_close > 0:
                    amount_to_close, rtn = self._close_individual_trade_on_new_order(trade, order, amount_to_close, rtn)

        if amount_to_close > 0:  # TODO: how to pass min_amount?
            # self._logger.error("The order size is bigger than any trade. {amount_to_close} left to close of {order.amount}.")
            pass

        return rtn

    def register_new_order_on_trades(self, order: Order):
        if order is None:
            raise "Order can't be None"

        # TODO OrderStatusType.canceled or rejected
        if order.status == OrderStatusType.canceled or order.status == OrderStatusType.rejected:
            raise "Order condition unhandled (canceled or rejected)"

        if order.side == OrderSide.buy:
            trade_id = self._new_trade_by_order(order)
            # order.parent_trade = trade_id
            self.budget.lock(order.cost)
            if order.status == OrderStatusType.closed:
                self.archived_orders.append(order)
            else:  # open & partials are active, budget is lock equally.
                self.active_orders.append(order)

        elif order.side == OrderSide.sell:
            if order.status == OrderStatusType.closed:
                rtn = self._close_trades_on_new_updated_order(order)
                self.budget.unlock(order.cost, rtn)
                self.archived_orders.append(order)
            else:
                # stop loss => if order.stop_price and order.stop_price > 0:
                # TODO: budget.unlock (partial) ???
                self.active_orders.append(order)
        else:
            raise "Order condition unhandled (OrderSide)"

    def update_trades_on_update_orders(self, order: Order):
        if order is None:
            raise "Order can't be None"

        if order.status == OrderStatusType.rejected:
            # on rejected
            #   => problem... the market could be closed.
            #   keep processing trades
            # self._logger.error(f"Order {order.id} was rejected. Bot: {self.bot_id}")
            # self._notifications_manager.high(f"Order {order.id} was rejected. Bot: {self.bot_id}")
            pass

        if order.side == OrderSide.buy:
            if order.status == OrderStatusType.closed:
                # on buy, close
                #   update trade.order status (done in _update_orders_status)
                # nothing to do here
                pass
            elif order.status == OrderStatusType.canceled or order.status == OrderStatusType.rejected:
                # on buy, cancel or rejected
                #   archive trade
                trade_found = False
                for trade in self.active_trades[:]:
                    if trade.entry_order_id == order.id:
                        self.active_trades.remove(trade)
                        trade.exit_time = order.timestamp
                        trade.exit_price = 0
                        trade.exit_order_id = order.status
                        self.closed_trades.append(trade)
                        trade_found = True
                if not trade_found:
                    # self._logger.error(f"Order {order.id} canceled or rejected not found in trades. Bot: {self.bot_id}")
                    pass

                # TODO order.cost is set on cancel and reject?
                self.budget.unlock(order.cost, 0.0)
            elif order.status == OrderStatusType.open:  # open & partials are active, budget is lock equally.
                # on buy, open or partial
                #   update trade.order status (done in _update_orders_status)
                # nothing to do here
                pass
            else:
                raise "Order condition unhandled (OrderSide.buy)"

        elif order.side == OrderSide.sell:
            if order.status == OrderStatusType.closed:
                # on sell, close
                #   close trade... _close_trades_on_new_updated_order?
                rtn = self._close_trades_on_new_updated_order(order)
                self.budget.unlock(order.cost, rtn)

            elif order.status == OrderStatusType.canceled or order.status == OrderStatusType.rejected:
                # on sell, cancel or rejected
                #   do nothing unless partial
                # TODO: if a partial order is cancelled... what should be done?
                pass
            elif order.status == OrderStatusType.open:
                # on sell, partial
                #   update trade.order status (done in _update_orders_status)
                #   budget.unlock(partial)? => risky
                # stop loss => if order.stop_price and order.stop_price > 0:
                # TODO: budget.unlock (partial) ???
                pass
            else:
                raise "Order condition unhandled (OrderSide.sell)"
        else:
            raise "Order condition unhandled (OrderSide)"

    def archive_order_on_cancel(self, order: Order):
        found_order = False
        for loop_order in self.active_orders[:]:
            if loop_order.id == order.id:
                self.active_orders.remove(loop_order)
                found_order = True
        if not found_order:
            # self._logger.error(f"Order {order.id} canceled but not found in active_orders. Bot: {self.bot_id}")
            pass
        self.archived_orders.append(order)
        self.update_trades_on_update_orders(order)  # TODO: check
