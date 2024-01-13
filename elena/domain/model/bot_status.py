import time
from typing import List, Optional

from pydantic import BaseModel, Field

from elena.domain.model.order import Order, OrderSide, OrderStatusType
from elena.domain.model.trade import Trade


class BotBudget(BaseModel):
    # Budget in quote to spend in the strategy.
    # TODO: make free, used and budget_control read only
    free: float = 0.0
    used: float = 0.0
    budget_control: bool = False

    def set(self, budget: float):
        self.free = budget
        self.used = 0.0
        self.budget_control = (budget > 0)

    def lock(self, used: float):
        if self.budget_control and self.free > used:
            # raise? return false? as it is now the operation si already done...
            pass
        self.free = self.free - used
        self.used = self.used + used

    def unlock(self, released: float):
        if self.budget_control and self.used > released:
            # think!
            pass
        self.free = self.free + released
        self.used = self.used - released

    # @property
    # def free(self):
    #     return self._free
    #
    # @property
    # def used(self):
    #     return self._used

    @property
    def total(self) -> float:
        return self.free + self.used

    @property
    def is_budget_controlled(self) -> bool:
        return self.budget_control


class BotStatus(BaseModel):
    bot_id: str
    timestamp: int = int(time.time() * 1000)
    active_orders: List[Order]
    archived_orders: List[Order]
    active_trades: List[Trade]
    closed_trades: List[Trade]
    budget: BotBudget

    def _new_trade_by_order(self, order: Order):
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

    @staticmethod
    def _get_precision(f1: float) -> int:
        # https://stackoverflow.com/questions/3018758/determine-precision-and-scale-of-particular-number-in-python
        # TODO: review solution
        str1 = str(f1)
        return len(str1.split(".")[1])

    @staticmethod
    def _calc_update_trade_return_and_duration(trade: Trade) -> float:
        trade.duration = trade.exit_time - trade.entry_time
        trade.return_pct = trade.exit_price / trade.entry_price
        cash_rtn = trade.exit_cost - trade.entry_cost
        return cash_rtn

    def _close_individual_trade_on_new_order(self, trade: Trade, order: Order, amount_to_close: float, rtn: float) -> (float, float):
        size_precision = self._get_precision(trade.size)  # done to avoid a call to Exchange to round amount_to_close at retrun
        if trade.size <= round(amount_to_close, size_precision):
            self.active_trades.remove(trade)
            trade.exit_time = order.timestamp
            trade.exit_price = order.average
            trade.exit_cost = order.cost
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
            self._new_trade_by_order(order)
            self.budget.lock(order.cost)
            if order.status == OrderStatusType.closed:
                self.archived_orders.append(order)
            else:  # open & partials are active, budget is lock equally.
                self.active_orders.append(order)

        elif order.side == OrderSide.sell:
            if order.status == OrderStatusType.closed:
                rtn = self._close_trades_on_new_updated_order(order)
                # TODO profit control in budget
                self.budget.unlock(order.cost)
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
                self.budget.unlock(order.cost)
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
                # TODO profit control in budget
                self.budget.unlock(order.cost)

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
