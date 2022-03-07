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
        self._state['buy'] = 0.0
        self._state['buy_order_id'] = ''
        self._state['buy_order'] = None
        self._state['sell'] = 0.0
        self._state['sell_order_id'] = ''
        self._state['sell_order'] = None
        self._state['status'] = ''
        self._state['iteration_benefit'] = 0.0
        self._state['iteration_margin'] = 0.0
        self._state['iteration_current_bid'] = 0
        self._state['iteration_current_ask'] = 0
        self._state['iteration_current_value'] = 0
        self._state['iteration_current_value_BUSD'] = 0
        self._state['iteration_current_margin'] = 0
        self._state['iteration_current_total_benefit'] = 0
        self._state['left_on_asset'] = 0.0
        self._state['sleep_until'] = 0
        self._state['sell_status'] = None

    def iterate(self):
        if self._state['sleep_until'] < get_time():
            if not self._state['buy_order_id'] and self._state['active']:
                buy, sell = self._estimate_buy_sel()
                if buy > 0:
                    llog("create a new buy order")
                    force_buy_price = self._state['algo'] > 7
                    new_buy_order = self._exchange.create_buy_order(self._state['max_order'], self._state['symbol'], buy, force_buy_price)
                    self._reset_state()
                    self._state['buy_order_id'] = new_buy_order['orderId']
                    self._state['buy_order'] = new_buy_order
                    self._state['buy'] = buy
                    self._state['sell'] = sell
                    self._state['status'] = 'buying'
                    self._save_state()
                else:
                    self._state['sleep_until'] = self._sleep_until(get_time(), 5)
                    self._state['status'] = "waiting - don't buy"
                    self._save_state()
                    llog("don't buy")
                # return --- maybe the order is executed immediately

            if self._state['buy_order_id'] and not self._state['sell_order_id']:
                self._update_orders_status_values_and_profits()
                buy_order = self._state['buy_order']
                status = buy_order['status']
                order_time = int(buy_order['time'])
                order_age_limit = order_time + (float(self._state['buy_auto_cancel_timeout']) * 60 * 1000)
                now = get_time()
                if status == OrderStatus.FILLED.value:
                    self._create_sell_order(self._state['sell'])
                elif status == OrderStatus.CANCELED.value:
                    llog("buy cancellation detected")
                    self._add_cycles()
                    self._save_history()
                    if self._state['active'] == 1:
                        self._reset_state()
                        self._state['status'] = 'buy cancellation'
                        self._save_state()
                    else:
                        self._delete_state()
                elif status == OrderStatus.NEW.value and now > order_age_limit:
                    llog("auto buy cancellation")
                    cancellation = self._exchange.cancel_order(self._state['symbol'], self._state['buy_order_id'])
                    llog(cancellation)
                    self._state['status'] = 'auto buy cancellation'
                    self._add_buy_auto_cancel_count()
                    self._save_state()
                else:
                    # self._state['sleep_until'] = self._sleep_until(get_time(), 2)
                    self._save_state()
                    llog("waiting purchase")
                # return --- maybe the order is executed immediately

            if self._state['buy_order_id'] and self._state['sell_order_id']:
                self._update_orders_status_values_and_profits()
                sell_order = self._state['sell_order']
                status = sell_order['status']
                sell_order_update_time = int(sell_order['updateTime'])
                order_age_limit = sell_order_update_time + (float(self._state['sell_auto_cancel_timeout']) * 60 * 1000)
                now = get_time()
                if status == OrderStatus.FILLED.value:
                    llog("save history")
                    self._add_sales()
                    self._save_history()
                    if self._state['active'] == 1:
                        llog("set sleep")
                        self._calculate_reinvest_or_losses()
                        self._reset_state()
                        self._state['sleep_until'] = self._sleep_until(sell_order_update_time, self._state['data_samples'] * self._state['sleep_until_factor'])
                        self._state['status'] = 'waiting'
                        self._save_state()
                    else:
                        self._save_state()
                        self._delete_state()
                elif status == OrderStatus.CANCELED.value:
                    llog("sell cancellation, save history")
                    self._state['status'] = 'manual sell cancellation'
                    self._add_cycles()
                    self._save_history()
                    self._save_state()
                    self._delete_state()
                elif status == OrderStatus.NEW.value and now > order_age_limit and float(self._state['sell_auto_cancel_timeout'])>0:
                    self._state['sell_status'] = "sell timeout"
                    buy_order = self._state['buy_order']
                    order_buy_price = float(buy_order['price'])  # get the real price when bought
                    order_sell_price = float(sell_order['price'])  # get the sell price as is in the exchange

                    bid = self._state['iteration_current_bid']
                    minimum_profit = 1 + ((self._exchange.minimum_profit-1)/2)
                    minimum_price = order_buy_price * minimum_profit

                    if bid >= minimum_price:  # earning
                        if self._state['sell_auto_cancel_im_feeling_lucky_data_samples'] > 0:
                            buy, sell = self._estimate_buy_sel(data_samples=self._state['sell_auto_cancel_im_feeling_lucky_data_samples'])
                            if sell > order_sell_price:
                                buy_order_id = self._state['buy_order_id']
                                text = f'Cancel and sell at higher price, ' \
                                       f'order_id:{buy_order_id}, ' \
                                       f'order_buy_price:{order_buy_price}, ' \
                                       f'order_sell_price:{order_sell_price}, new_sell_price:{sell}'
                                llog(text)
                                self._state['sell_status'] = text
                                self._cancel_sell_order_and_create_a_new_one(sell)
                                return
                            elif sell > 0:
                                llog("Sell time out but do nothing. set sleep to 0.")
                                self._state['sell_status'] = "Sell time out but do nothing. Tendence is high."
                                self._save_state()
                                return
                            else:
                                pass  # Cancel order and sell at bid (we get some benefit)
                        llog("Cancel order and sell at bid (we get some benefit)")
                        self._state['sell_status'] = "Cancel order and sell at bid (we get some benefit)"
                        self._cancel_sell_order_and_create_a_new_one(bid, force_sell_price=True)
                    else:  # loosing
                        percentage_loss = self._state['iteration_current_margin'] * -1
                        absolute_loss = (order_buy_price - bid) * float(sell_order['origQty'])
                        text = f'loss%:{percentage_loss}, order_buy_price:{order_buy_price}, bid:{bid}, loss$:{absolute_loss}'
                        llog(text)
                        self._state['sell_status'] = text
                        self._save_state()

                        stop_loss_percentage_absolute = (
                                self._state['stop_loss_percentage_absolute'] > 0 and
                                percentage_loss <= self._state['stop_loss_percentage_absolute'])

                        stop_loss_percentage_relative_to_accumulated_benefits = (
                                self._state['stop_loss_percentage_relative_to_accumulated_benefits'] > 0 and
                                absolute_loss <= (self._state['accumulated_benefit'] * (self._state['stop_loss_percentage_relative_to_accumulated_benefits'] / 100)))

                        if stop_loss_percentage_absolute or stop_loss_percentage_relative_to_accumulated_benefits:
                            text = f'Cancel order and sell at bid (losing:{percentage_loss}%,{absolute_loss}$)'
                            llog(text)
                            self._state['sell_status'] = text
                            self._cancel_sell_order_and_create_a_new_one(bid, force_sell_price=True)
                else:
                    self._state['sleep_until'] = self._sleep_until(get_time(), 5)
                    self._save_state()
                    llog("waiting sell")

                # return --- maybe the order is executed immediately
        else:
            llog("sleeping")

    @staticmethod
    def _verify_key_set_default(state, key, default_value):
        if state.get(key) is None:
            state[key] = default_value

    @staticmethod
    def _del_key(state, key):
        if not state.get(key) is None:
            del state[key]

    def _read_state(self):  # TODO: if it uses self._robot_filename why is not using self._state?
        fp = open(self._robot_filename, 'r')
        state = json.load(fp)
        fp.close()

        # default values
        self._verify_key_set_default(state, 'buy_order_id', 0)
        self._verify_key_set_default(state, 'sell_order_id', 0)
        self._verify_key_set_default(state, 'sleep_until', 0)
        self._verify_key_set_default(state, 'sleep_until_factor', 1.5)
        self._verify_key_set_default(state, 'buy_auto_cancel_timeout', 0)
        self._verify_key_set_default(state, 'buy_auto_cancel_count', 0)
        self._verify_key_set_default(state, 'iteration_current_bid', 0)
        self._verify_key_set_default(state, 'iteration_current_ask', 0)
        self._verify_key_set_default(state, 'iteration_current_value', 0)
        self._verify_key_set_default(state, 'iteration_current_value_BUSD', 0)
        self._verify_key_set_default(state, 'iteration_current_margin', 0)
        self._verify_key_set_default(state, 'iteration_current_total_benefit', 0)
        self._verify_key_set_default(state, 'sell_auto_cancel_timeout', 0)
        self._verify_key_set_default(state, 'sell_auto_cancel_count', 0)
        self._verify_key_set_default(state, 'sell_auto_cancel_im_feeling_lucky_data_samples', 0)
        self._verify_key_set_default(state, 'sell_auto_cancel_lucky_count', 0)
        self._verify_key_set_default(state, 'stop_loss_percentage_absolute', 0)
        self._verify_key_set_default(state, 'stop_loss_percentage_relative_to_accumulated_benefits', 0)
        self._verify_key_set_default(state, 'reinvest', 0)
        self._verify_key_set_default(state, 'accumulated_benefit', 0)
        self._verify_key_set_default(state, 'accumulated_benefit_BUSD', 0)
        self._verify_key_set_default(state, 'accumulated_margin', 0)

        self._verify_key_set_default(state, 'sales', 0)
        self._verify_key_set_default(state, 'cycles', 0)

        # migration
        if state['active'] == 1:
            if state['buy_auto_cancel_timeout'] == state['data_samples']:
                state['buy_auto_cancel_timeout'] = 5

            if state['sell_auto_cancel_timeout'] == state['data_samples']:
                if state['algo'] == 8 or state['algo'] == 9:
                    state['sell_auto_cancel_timeout'] = int(state['margin'] * 0.75) + 1
                    if state['sell_auto_cancel_im_feeling_lucky_data_samples'] > 0:
                        state['sell_auto_cancel_im_feeling_lucky_data_samples'] = int(state['margin']) if int(state['margin']) >= 5 else 5

            state['stop_loss_percentage_relative_to_accumulated_benefits'] = 0

        # bug correction
        if state['sales'] > state['cycles']:
            state['sales'] = state['cycles']
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

    def _add_cycles(self):
        self._state['cycles'] = self._state['cycles'] + 1

    def _add_sales(self):
        self._add_cycles()
        self._state['sales'] = self._state['sales'] + 1

    def _add_buy_auto_cancel_count(self):
        self._state['buy_auto_cancel_count'] = self._state['buy_auto_cancel_count'] + 1

    def _add_sell_auto_cancel_count(self):
        self._state['sell_auto_cancel_count'] = self._state['sell_auto_cancel_count'] + 1

    def _add_sell_auto_cancel_lucky_count(self):
        self._state['sell_auto_cancel_lucky_count'] = self._state['sell_auto_cancel_lucky_count'] + 1

    def _update_orders_status_values_and_profits(self):
        buy_order = ''
        sell_order = ''
        iteration_benefit = 0
        iteration_margin = 0
        left_on_asset = 0

        if self._state['buy_order_id']:
            check_order = True
            if self._state['buy_order']:
                buy_order = self._state['buy_order']
                status = buy_order['status']
                check_order = not (status == OrderStatus.FILLED.value)
            if check_order:
                buy_order = self._exchange.get_order(self._state['buy_order_id'], self._state['symbol'])
                self._state['buy_order'] = buy_order

            if self._state['sell_order_id']:
                sell_order = self._exchange.get_order(self._state['sell_order_id'], self._state['symbol'])
                self._state['sell_order'] = sell_order
                if sell_order['status'] == OrderStatus.FILLED.value:
                    iteration_benefit = float(sell_order['cummulativeQuoteQty']) - float(buy_order['cummulativeQuoteQty'])
                    iteration_margin = (iteration_benefit / float(buy_order['cummulativeQuoteQty'])) * 100
                    left_on_asset = float(buy_order['executedQty']) - float(sell_order['executedQty'])

                if sell_order['status'] == OrderStatus.NEW.value:
                    bid, ask = self._exchange.get_cached_order_book_first_bids_asks(self._state['symbol'])
                    self._state['iteration_current_bid'] = bid
                    self._state['iteration_current_ask'] = ask

                    buy_order = self._state['buy_order']
                    order_buy_price = float(buy_order['price'])  # get the real price when bought
                    self._state['iteration_current_margin'] = (bid / order_buy_price) * 100 - 100

                    self._state['iteration_current_value'] = bid * float(sell_order['origQty'])
                    if self._state['symbol'].endswith('BUSD'):
                        self._state['iteration_current_value_BUSD'] = self._state['iteration_current_value']
                    else:
                        self._state['iteration_current_value_BUSD'] = self._state['iteration_current_value'] * self._exchange.get_cached_avg_price(self._state['symbol'])
                    self._state['iteration_current_total_benefit'] = self._state['accumulated_benefit'] + self._state['iteration_current_value'] - self._state['max_order']



        self._state['iteration_benefit'] = iteration_benefit
        self._state['iteration_margin'] = iteration_margin
        self._state['left_on_asset'] = left_on_asset

        if iteration_benefit != 0:
            self._state['accumulated_benefit'] = self._state['accumulated_benefit'] + iteration_benefit
            if self._state['symbol'].endswith('BUSD'):
                self._state['accumulated_benefit_BUSD'] = self._state['accumulated_benefit']
            else:
                self._state['accumulated_benefit_BUSD'] = self._state['accumulated_benefit'] * self._exchange.get_cached_avg_price(self._state['symbol'])
            self._state['accumulated_margin'] = self._state['accumulated_margin'] + iteration_margin
            if iteration_benefit < 0:
                llog("iteration margin <0!", self._state)

    def _save_history(self):
        self._update_orders_status_values_and_profits()

        history_state = dict(self._state)
        filename = f"history/{str(get_time())}_{str(history_state['buy_order_id'])}.json"

        history_state['active'] = -1

        fp = open(filename, 'w')
        json.dump(history_state, fp)
        fp.close()

    def _calculate_reinvest_or_losses(self):
        # re-invest
        if self._state['reinvest'] > 0 and self._state['iteration_benefit'] > 0:
            self._state['max_order'] = self._state['max_order'] + (self._state['iteration_benefit'] * self._state['reinvest'] / 100)

        # losses
        if self._state['iteration_benefit'] < 0:
            self._state['max_order'] = self._state['max_order'] + self._state['iteration_benefit']

        # temporary algo migration for testing
        if self._state['algo'] == 4 or self._state['algo'] == 6:
            self._state['algo'] = 8
        if self._state['algo'] == 5 or self._state['algo'] == 7:
            self._state['algo'] = 9

    def _create_sell_order(self, sell, force_sell_price=False):
        buy_order = self._state['buy_order']
        sell_quantity = float(buy_order['executedQty'])
        new_sell_order = self._exchange.create_sell_order(self._state['symbol'], sell_quantity, sell, force_sell_price)
        if new_sell_order:
            llog("created a new sell order", new_sell_order)
            self._state['sell_order_id'] = new_sell_order['orderId']
            self._state['sell_order'] = new_sell_order
            self._state['status'] = 'selling'
            self._save_state()

    def _cancel_sell_order_and_create_a_new_one(self, sell, force_sell_price=False):
        cancellation = self._exchange.cancel_order(self._state['symbol'], self._state['sell_order_id'])
        llog(cancellation)
        if sell < self._state['sell']:
            self._add_sell_auto_cancel_count()
        else:
            self._add_sell_auto_cancel_lucky_count()
        self._state['sell_order_id'] = 0
        self._save_state()  # TODO: review if it's necessary... if the order was canceled but the new one can't be executed in the next iteration this would be understood as a human cancelation.
        self._create_sell_order(sell, force_sell_price)

    def _estimate_buy_sel(self, data_samples=None):
        if data_samples is None:
            data_samples = self._state['data_samples']
        candles_df = self._exchange.get_candles(p_symbol=self._state['symbol'], p_limit=data_samples)
        return self._buy_sell(candles_df, self._state['algo'], self._state['margin'], self._state['tendence_tolerance'])

    @staticmethod
    def _sleep_until(sell_execution_time, minutes):
        return sell_execution_time + minutes * 60 * 1000  # 45' after the sale

    @staticmethod
    def _ensure_sell_is_higher_than_buy_by(next_sell, next_buy, minimum_profit):
        # ensure sell is higher than buy at least by 5 per thousand to pay fees
        if next_sell / next_buy > minimum_profit:
            buy = next_buy
            sell = next_sell
        else:
            buy = 0
            sell = 0
        return buy, sell

    @staticmethod
    def _sell_based_on_linear_regression(candles_df_buy_sell, sell_field, margin=0):
        # TODO: reusing margin but is the number of steps to extrapolate
        regression_close = np.polyfit(candles_df_buy_sell.index, candles_df_buy_sell[sell_field], 1)
        return regression_close[0] * (candles_df_buy_sell.index[-1] + 1 + margin) + regression_close[1]

    def _buy_sell_based_on_linear_regression(self, candles_df_buy_sell, sell_field, margin=0):
        regression_low = np.polyfit(candles_df_buy_sell.index, candles_df_buy_sell["Low"], 1)
        next_low = regression_low[0] * (candles_df_buy_sell.index[-1] + 1) + regression_low[1]

        next_close = self._sell_based_on_linear_regression(candles_df_buy_sell, sell_field, margin=margin)

        buy, sell = Elena._ensure_sell_is_higher_than_buy_by(next_close, next_low, self._exchange.minimum_profit)
        return buy, sell

    def _buy_on_bid_sell_based_on_linear_regression(self, candles_df_buy_sell, sell_field, margin=0):
        next_low, ask = self._exchange.get_cached_order_book_first_bids_asks(self._state['symbol'])

        next_close = self._sell_based_on_linear_regression(candles_df_buy_sell, sell_field, margin=margin)

        buy, sell = Elena._ensure_sell_is_higher_than_buy_by(next_close, next_low, self._exchange.minimum_profit)
        return buy, sell

    def _buy_on_bid_sell_based_on_fixed_margin(self, margin):
        buy, ask = self._exchange.get_cached_order_book_first_bids_asks(self._state['symbol'])

        sell = buy * (1 + (margin / 100))

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
                buy, sell = self._buy_sell_based_on_linear_regression(candles_df_buy_sell, "Close", margin=0)
            if algo == 5:
                buy, sell = self._buy_sell_based_on_linear_regression(candles_df_buy_sell, "High", margin=0)
            if algo == 6:
                buy, sell = self._buy_sell_based_on_linear_regression(candles_df_buy_sell, "Close", margin=margin)
            if algo == 7:
                buy, sell = self._buy_sell_based_on_linear_regression(candles_df_buy_sell, "High", margin=margin)
            if algo == 8:
                buy, sell = self._buy_on_bid_sell_based_on_linear_regression(candles_df_buy_sell, "Close", margin=margin)
            if algo == 9:
                buy, sell = self._buy_on_bid_sell_based_on_linear_regression(candles_df_buy_sell, "High", margin=margin)
            if algo == 10:
                buy, sell = self._buy_on_bid_sell_based_on_fixed_margin(margin)
        if algo == 3:
            buy, sell = self._buy_sell_based_on_linear_regression(candles_df_buy_sell, "Close", margin=0)

        return buy, sell
