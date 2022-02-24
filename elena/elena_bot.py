import json
import os

import numpy as np

from elena.exchange import Exchange, OrderStatus
from elena.logging import llog
from elena.utils import get_time


class Elena:
    def __init__(self, robot_filename: str, exchange: Exchange):
        self._robot_filename = robot_filename
        self._exchange = exchange
        self._state = self._read_state()

    def _reset_state(self):
        self._state['sleep_until'] = 0
        self._state['buy_order_id'] = ''
        self._state['sell_order_id'] = ''
        self._state['buy'] = 0
        self._state['sell'] = 0
        self._state['status'] = ''

    def iterate(self):
        if self._state['sleep_until'] < get_time():
            if not self._state['buy_order_id'] and self._state['active']:
                buy, sell = self._estimate_buy_sel(self._state)
                if buy > 0:
                    llog("create a new buy order")
                    new_buy_order_id = self._exchange.create_buy_order(self._state['max_order'], self._state['symbol'], buy)
                    self._reset_state()
                    self._state['buy_order_id'] = new_buy_order_id
                    self._state['buy'] = buy
                    self._state['sell'] = sell
                    self._state['status'] = 'buying'
                    self._save_state()
                else:
                    self._state['sleep_until'] = self._sleep_until(get_time(), 5)
                    self._state['status'] = "waiting - don't buy"
                    self._save_state()
                    llog("don't buy")
                return

            if self._state['buy_order_id'] and not self._state['sell_order_id']:
                new_sell_order_id = self._exchange.create_sell_order(self._state['symbol'], self._state['buy_order_id'],
                                                                     self._state['sell'])
                if new_sell_order_id:
                    llog("create a new sell order")
                    self._state['sell_order_id'] = new_sell_order_id
                    self._state['status'] = 'selling'
                    self._save_state()
                else:
                    status, order_update_time = self._exchange.check_order_status(self._state['symbol'],
                                                                                  self._state['buy_order_id'])
                    if not status == OrderStatus.CANCELED.value:
                        self._state['sleep_until'] = self._sleep_until(get_time(), 5)
                        self._save_state()
                        llog("waiting purchase")
                    else:
                        llog("buy cancellation")
                        self._save_history_state_and_profit()
                        if self._state['active'] == 1:
                            self._reset_state()
                            self._state['status'] = 'buy cancellation'
                            self._save_state()
                        else:
                            self._delete_state()
                return

            if self._state['buy_order_id'] and self._state['sell_order_id']:
                status, order_update_time = self._exchange.check_order_status(self._state['symbol'], self._state['sell_order_id'])
                if status == OrderStatus.FILLED.value:
                    llog("save history")
                    self._save_history_state_and_profit()
                    if self._state['active'] == 1:
                        llog("set sleep")
                        self._reset_state()
                        self._state['sleep_until'] = self._sleep_until(order_update_time, self._state['data_samples'] * 1.5)
                        self._state['status'] = 'waiting'
                        self._save_state()
                    else:
                        self._save_state()
                        self._delete_state()
                elif status == OrderStatus.CANCELED.value:
                    llog("sell cancellation, save history")
                    self._state['status'] = 'sell cancellation'
                    self._save_history_state_and_profit()
                    self._save_state()
                    self._delete_state()
                else:
                    self._state['sleep_until'] = self._sleep_until(get_time(), 5)
                    self._save_state()
                    llog("waiting sell")
                return
        else:
            llog("sleeping")

    def _read_state(self):
        fp = open(self._robot_filename, 'r')
        state = json.load(fp)
        fp.close()
        return state

    def _save_state(self, state=None, filename=None):
        if not filename:
            filename = self._robot_filename
        if not state:
            state = self._state
        fp = open(filename, 'w')
        json.dump(state, fp)
        fp.close()

    def _delete_state(self):
        os.rename(self._robot_filename, self._robot_filename + '.inactive')

    def _save_history_state_and_profit(self):
        buy_order = ''
        sell_order = ''
        iteration_benefit = 0
        iteration_margin = 0
        left_on_asset = 0

        if self._state['buy_order_id']:
            buy_order = self._exchange.get_order(self._state['buy_order_id'], self._state['symbol'])
            if self._state['sell_order_id']:
                sell_order = self._exchange.get_order(self._state['sell_order_id'], self._state['symbol'])
                if sell_order['status'] == OrderStatus.FILLED.value:
                    iteration_benefit = float(sell_order['cummulativeQuoteQty']) - float(
                        buy_order['cummulativeQuoteQty'])
                    iteration_margin = (iteration_benefit / float(buy_order['cummulativeQuoteQty'])) * 100
                    left_on_asset = float(buy_order['executedQty']) - float(sell_order['executedQty'])

        if self._state.get('accumulated_benefit') is None:
            self._state['accumulated_benefit'] = 0
        if self._state.get('accumulated_margin') is None:
            self._state['accumulated_margin'] = 0
        if self._state.get('sales') is None:
            self._state['sales'] = 0
        if self._state.get('cycles') is None:
            self._state['cycles'] = 0

        self._state['accumulated_benefit'] = self._state['accumulated_benefit'] + iteration_benefit
        self._state['accumulated_margin'] = self._state['accumulated_margin'] + iteration_margin
        if iteration_benefit != 0:
            self._state['sales'] = self._state['sales'] + 1
        self._state['cycles'] = self._state['cycles'] + 1

        history_state = dict(self._state)
        filename = f"history/{str(get_time())}_{str(history_state['buy_order_id'])}.json"

        history_state['active'] = -1
        history_state['buy_order'] = buy_order
        history_state['sell_order'] = sell_order
        history_state['iteration_benefit'] = iteration_benefit
        history_state['iteration_margin'] = iteration_margin
        history_state['left_on_asset'] = left_on_asset

        fp = open(filename, 'w')
        json.dump(history_state, fp)
        fp.close()

        # TODO: refactor this method. It's doing more than one thing.
        # re-invest
        if self._state.get('reinvest') is not None:
            if self._state['reinvest'] > 0 and iteration_benefit > 0:
                self._state['max_order'] = self._state['max_order'] + (iteration_benefit * self._state['reinvest'] / 100)

        if iteration_benefit < 0:
            llog("iteration margin <0!", history_state)

        # temporary algo migration for testing
        if self._state['algo'] == 4 or self._state['algo'] == 6:
            self._state['algo'] = 8
        if self._state['algo'] == 5 or self._state['algo'] == 7:
            self._state['algo'] = 9

    def _estimate_buy_sel(self, state):
        candles_df = self._exchange.get_candles(p_symbol=state['symbol'], p_limit=state['data_samples'])
        return self._buy_sell(candles_df, state['algo'], state['margin'], state['tendence_tolerance'])

    @staticmethod
    def _sleep_until(sell_execution_time, minutes):
        return sell_execution_time + minutes * 60 * 1000  # 45' after the sale

    @staticmethod
    def _ensure_sell_is_higher_than_buy_by(next_sell, next_buy, minimum_profit=1.0005):
        # ensure sell is higher than buy at least by 5 per thousand to pay fees
        if next_sell / next_buy > minimum_profit:
            buy = next_buy
            sell = next_sell
        else:
            buy = 0
            sell = 0
        return buy, sell

    @staticmethod
    def _buy_sell_based_on_linear_regression(candles_df_buy_sell, sell_field, margin=0):
        regression_low = np.polyfit(candles_df_buy_sell.index, candles_df_buy_sell["Low"], 1)
        next_low = regression_low[0] * (candles_df_buy_sell.index[-1] + 1) + regression_low[1]

        # TODO: reusing margin but is the number of steps to extrapolate
        regression_close = np.polyfit(candles_df_buy_sell.index, candles_df_buy_sell[sell_field], 1)
        next_close = regression_close[0] * (candles_df_buy_sell.index[-1] + 1 + margin) + regression_close[1]

        buy, sell = Elena._ensure_sell_is_higher_than_buy_by(next_close, next_low)
        return buy, sell

    def _buy_on_bid_sell_based_on_linear_regression(self, candles_df_buy_sell, sell_field, margin=0):
        next_low, ask = self._exchange.get_order_book_first_bids_asks(self._state['symbol'])

        # TODO: reusing margin but is the number of steps to extrapolate
        regression_close = np.polyfit(candles_df_buy_sell.index, candles_df_buy_sell[sell_field], 1)
        next_close = regression_close[0] * (candles_df_buy_sell.index[-1] + 1 + margin) + regression_close[1]

        buy, sell = Elena._ensure_sell_is_higher_than_buy_by(next_close, next_low)
        return buy, sell

    def _buy_sell(self, candles_df_buy_sell, algo, margin, tendence_tolerance):
        sell = 0
        buy = 0

        regression = np.polyfit(candles_df_buy_sell.index, candles_df_buy_sell["Close"], 1)
        tendency = regression[0]

        if tendency > tendence_tolerance:
            if algo == 0:
                avg_price = candles_df_buy_sell["Close"].mean()
                margin_local = margin * (2 / 3)
                buy = avg_price * (1 - ((margin_local / 2) / 100))
                buy = buy.astype(float)
                sell = avg_price * (1 + (margin_local / 100))
            if algo == 1:
                buy = candles_df_buy_sell['Close'][candles_df_buy_sell.index[-1]]
                buy = buy.astype(float)
                sell = buy * (1 + (margin / 100))
            if algo == 2:
                buy = candles_df_buy_sell['High'][candles_df_buy_sell.index[-1]]
                buy = buy.astype(float)
                sell = buy * (1 + (margin / 100))
            if algo == 4:
                buy, sell = Elena._buy_sell_based_on_linear_regression(candles_df_buy_sell, "Close", margin=0)
            if algo == 5:
                buy, sell = Elena._buy_sell_based_on_linear_regression(candles_df_buy_sell, "High", margin=0)
            if algo == 6:
                buy, sell = Elena._buy_sell_based_on_linear_regression(candles_df_buy_sell, "Close", margin=margin)
            if algo == 7:
                buy, sell = Elena._buy_sell_based_on_linear_regression(candles_df_buy_sell, "High", margin=margin)
            if algo == 8:
                buy, sell = self._buy_on_bid_sell_based_on_linear_regression(candles_df_buy_sell, "Close", margin=margin)
            if algo == 9:
                buy, sell = self._buy_on_bid_sell_based_on_linear_regression(candles_df_buy_sell, "High", margin=margin)
        if algo == 3:
            buy, sell = Elena._buy_sell_based_on_linear_regression(candles_df_buy_sell, "Close", margin=0)

        return buy, sell
