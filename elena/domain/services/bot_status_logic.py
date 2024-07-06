import time
from typing import Tuple

from elena.domain.model.bot_status import BotStatus
from elena.domain.model.order import Order, OrderSide, OrderStatusType
from elena.domain.model.trade import Trade
from elena.domain.ports.logger import Logger
from elena.domain.ports.metrics_manager import MetricsManager
from elena.domain.ports.notifications_manager import NotificationsManager


class BotStatusLogic:
    def __init__(self, logger: Logger, metrics_manager: MetricsManager, notifications_manager: NotificationsManager, precision_amount: int, precision_price: int):
        self._logger = logger
        self._metrics_manager = metrics_manager
        self._notifications_manager = notifications_manager
        self.precision_amount = precision_amount
        self.precision_price = precision_price

    @staticmethod
    def _new_trade_by_order(bot_status: BotStatus, order: Order) -> Tuple[BotStatus, str]:
        # All Trades start/"born" here...
        new_trade = Trade(
            exchange_id=order.exchange_id,
            bot_id=bot_status.bot_id,
            strategy_id=order.strategy_id,
            pair=order.pair,
            size=order.amount,
            entry_order_id=order.id,
            entry_price=order.average,
            entry_cost=order.cost,
            entry_time=order.timestamp,
            exit_order_id="0",  # TODO define an OrderId.Null
            exit_price=0.0,
            exit_cost=0.0,
        )
        new_trade.id = str(int(time.time() * 1000))  # TODO: improve trade.id auto generation
        bot_status.active_trades.append(new_trade)
        return bot_status, new_trade.id

    @staticmethod
    def _calc_update_trade_return_and_duration(trade: Trade) -> float:
        trade.duration = trade.exit_time - trade.entry_time  # type: ignore
        trade.profit = trade.exit_cost - trade.entry_cost  # type: ignore
        trade.return_pct = (trade.profit / trade.entry_cost) * 100
        return trade.profit

    def _close_individual_trade_on_new_order(
        self,
        bot_status: BotStatus,
        trade: Trade,
        order: Order,
        amount_to_close: float,
        rtn: float,
    ) -> [float, float]:  # type: ignore
        if trade.size <= round(amount_to_close, self.precision_amount):
            bot_status.active_trades.remove(trade)
            trade.exit_order_id = order.id
            trade.exit_time = order.timestamp
            trade.exit_price = order.average
            trade.exit_cost = round(order.cost * (trade.size / order.amount), self.precision_price)  # type: ignore
            individual_rtn = round(self._calc_update_trade_return_and_duration(trade), self.precision_price)
            rtn = rtn + individual_rtn
            bot_status.closed_trades.append(trade)
            self._notifications_manager.medium(
                f"Closed trade for {trade.size} on {order.pair} with benefit of {individual_rtn}. Entry price at: {trade.entry_price}, exit price at: {trade.exit_price}. Entry cost at: {trade.entry_cost}, exit cost at: {trade.exit_cost}"
            )
            self._metrics_manager.gauge("benefit", bot_status.bot_id, individual_rtn, tags=["trades", f"exchange:{order.exchange_id.value}"])
            return round(amount_to_close - trade.size, self.precision_amount), rtn
        else:
            self._logger.error(f"Amount to close is insufficient for trade id:{trade.id} size: {trade.size} on order {order.id} size: {order.amount} with pending to close {amount_to_close}")
            return amount_to_close, rtn

    def _close_trades_on_new_updated_order(self, bot_status: BotStatus, order: Order) -> float:
        amount_to_close = order.amount
        rtn = 0.0
        # check trades with an exit order id
        for trade in bot_status.active_trades[:]:
            if trade.exit_order_id == order.id and amount_to_close > 0:
                amount_to_close, rtn = self._close_individual_trade_on_new_order(bot_status, trade, order, amount_to_close, rtn)

        # check trades without an exit order id
        if amount_to_close > 0:
            for trade in bot_status.active_trades[:]:
                if trade.exit_order_id == "0" and amount_to_close > 0:  # TODO define an OrderId.Null
                    amount_to_close, rtn = self._close_individual_trade_on_new_order(bot_status, trade, order, amount_to_close, rtn)

        # close trade even with a different order_id
        if amount_to_close > 0:
            self._logger.warning("The order size is bigger than the trades with an explicit order_id or a blank order_id")
            for trade in bot_status.active_trades[:]:
                if amount_to_close > 0:
                    amount_to_close, rtn = self._close_individual_trade_on_new_order(bot_status, trade, order, amount_to_close, rtn)

        if amount_to_close > 0:  # TODO: how to pass min_amount?
            self._logger.error(f"The order size is bigger than any trade. {amount_to_close} left to close of {order.amount}.")
            pass

        return rtn

    def register_new_order_on_trades(self, bot_status: BotStatus, order: Order) -> BotStatus:
        if order is None:
            raise "Order can't be None"

        # TODO OrderStatusType.canceled or rejected
        if order.status == OrderStatusType.canceled or order.status == OrderStatusType.rejected:
            raise RuntimeError("Order condition unhandled (canceled or rejected)")

        if order.side == OrderSide.buy:
            bot_status, new_trade_id = self._new_trade_by_order(bot_status, order)
            # order.parent_trade = new_trade_id
            bot_status.budget.lock(order.cost)  # type: ignore
            if order.status == OrderStatusType.closed:
                bot_status.archived_orders.append(order)
            else:  # open & partials are active, budget is lock equally.
                bot_status.active_orders.append(order)

        elif order.side == OrderSide.sell:
            if order.status == OrderStatusType.closed:
                rtn = self._close_trades_on_new_updated_order(bot_status, order)
                bot_status.budget.unlock(order.cost, rtn)  # type: ignore
                bot_status.archived_orders.append(order)
            else:
                # stop loss => if order.stop_price and order.stop_price > 0:
                # TODO: budget.unlock (partial) ???
                bot_status.active_orders.append(order)
        else:
            raise RuntimeError("Order condition unhandled (OrderSide)")
        return bot_status

    def update_trades_on_update_orders(self, bot_status: BotStatus, order: Order) -> BotStatus:
        if order is None:
            raise "Order can't be None"

        if order.status == OrderStatusType.rejected:
            # on rejected
            #   => problem... the market could be closed.
            #   keep processing trades
            self._logger.error(f"Order {order.id} was rejected. Bot: {bot_status.bot_id}")
            self._notifications_manager.high(f"Order {order.id} was rejected. Bot: {bot_status.bot_id}")
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
                for trade in bot_status.active_trades[:]:
                    if trade.entry_order_id == order.id:
                        bot_status.active_trades.remove(trade)
                        trade.exit_time = order.timestamp
                        trade.exit_price = 0
                        trade.exit_order_id = order.status
                        bot_status.closed_trades.append(trade)
                        trade_found = True
                if not trade_found:
                    self._logger.error(f"Order {order.id} canceled or rejected not found in trades. Bot: {bot_status.bot_id}")
                    pass

                # TODO order.cost is set on cancel and reject?
                bot_status.budget.unlock(order.cost, 0.0)  # type: ignore
            elif order.status == OrderStatusType.open:  # open & partials are active, budget is lock equally.
                # on buy, open or partial
                #   update trade.order status (done in _update_orders_status)
                # nothing to do here
                pass
            else:
                raise RuntimeError("Order condition unhandled (OrderSide.buy)")

        elif order.side == OrderSide.sell:
            if order.status == OrderStatusType.closed:
                # on sell, close
                #   close trade... _close_trades_on_new_updated_order?
                rtn = self._close_trades_on_new_updated_order(bot_status, order)
                bot_status.budget.unlock(order.cost, rtn)  # type: ignore

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
                raise RuntimeError("Order condition unhandled (OrderSide.sell)")
        else:
            raise RuntimeError("Order condition unhandled (OrderSide)")

        return bot_status

    def archive_order_on_cancel(self, bot_status: BotStatus, order: Order) -> BotStatus:
        found_order = False
        for loop_order in bot_status.active_orders[:]:
            if loop_order.id == order.id:
                bot_status.active_orders.remove(loop_order)
                found_order = True
        if not found_order:
            # self._logger.error(f"Order {order.id} canceled but not found in active_orders. Bot: {self.bot_id}")
            pass
        bot_status.archived_orders.append(order)
        return self.update_trades_on_update_orders(bot_status, order)  # TODO: check
