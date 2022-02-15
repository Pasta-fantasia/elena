import time

import pandas as pd
from binance import Client
from mockito import when, mock
import json
from elena.binance import Binance
from elena.exchange import Exchange


def load_test_data(filePath: str) -> dict:
    with open(filePath) as json_file:
        data = json.load(json_file)
    return data


# Record test data for method get_candles
# Remove the '_' to run on tests
def _test_record_get_candles():
    binance = Binance()
    sut = Exchange(binance)
    sut.get_candles(p_symbol='ETHBUSD', p_interval=Client.KLINE_INTERVAL_1MINUTE, p_limit=10)


# Test method get_candles with get_klines mock based on previously recorded data
def test_get_candles():
    get_klines_data = load_test_data('../test_data/1644868841483-get_klines.json')
    api_mock = mock(spec=Binance)
    when(api_mock).get_klines(
        p_interval=get_klines_data['input']['p_interval'],
        p_limit=get_klines_data['input']['p_limit'],
        p_symbol=get_klines_data['input']['p_symbol'],
    ).thenReturn(get_klines_data['output'])

    get_candles_data = load_test_data('../test_data/1644868841486-get_candles.json')
    sut = Exchange(api_mock)
    actual = sut.get_candles(
        p_symbol=get_candles_data['input']['p_symbol'],
        p_interval=get_candles_data['input']['p_interval'],
        p_limit=get_candles_data['input']['p_limit'],
    )

    assert actual.to_json() == get_candles_data['output']
