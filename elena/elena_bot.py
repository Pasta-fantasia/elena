import json
import numpy as np


class Elena:
    @staticmethod
    def read_state(p_robot_filename):
        fp = open(p_robot_filename, 'r')
        state = json.load(fp)
        fp.close()
        return state

    @staticmethod
    def save_state(p_robot_filename, p_elena):
        fp = open(p_robot_filename, 'w')
        json.dump(p_elena, fp)
        fp.close()

    @staticmethod
    def estimate_buy_sel(exchange, p_elena, buy_sell_function):
        candles_df = exchange.get_candles(p_symbol=p_elena['symbol'], p_limit=p_elena['data_samples'])
        return buy_sell_function(candles_df, p_elena['algo'], p_elena['margin'], p_elena['tendence_tolerance'])

    @staticmethod
    def sleep_until(sell_execution_time, minutes):
        return sell_execution_time + minutes * 60 * 1000  # 45' after the sale
