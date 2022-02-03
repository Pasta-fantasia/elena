import time

import pandas as pd
from binance import Client
from mockito import when, mock
import json
from elena.binance import Binance
from elena.exchange import Exchange


def load_test_data(filename: str) -> dict:
    with open('../../test_data/' + filename) as json_file:
        data = json.load(json_file)
    return data


# Record test data for method get_candles
# Remove the '_' to run on tests
def _test_record_get_candles():
    binance = Binance()
    sut = Exchange(binance)
    sut.start_recorder()
    sut.get_candles(p_symbol='ETHBUSD', p_interval=Client.KLINE_INTERVAL_1MINUTE, p_limit=10)
    sut.stop_recorder()


# Test method get_candles with mocks based on previously recorded data
def test_get_candles():
    data = load_test_data('Exchange-1643865524441.json.data')
    api_mock = mock(spec=Binance)
    when(api_mock).get_klines(
        data['get_candles']['_api.get_klines']['input']['p_interval'],
        data['get_candles']['_api.get_klines']['input']['p_limit'],
        data['get_candles']['_api.get_klines']['input']['p_symbol'],
    ).thenReturn(data['get_candles']['_api.get_klines']['output']['candles'])

    sut = Exchange(api_mock)
    actual = sut.get_candles(
        data['get_candles']['input']['p_symbol'],
        data['get_candles']['input']['p_interval'],
        data['get_candles']['input']['p_limit'],
    )

    assert actual.to_json() == data['get_candles']['output']['candles_df']
