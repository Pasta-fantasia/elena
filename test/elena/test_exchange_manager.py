import json
from pathlib import Path

from binance import Client
from mockito import when, mock

from elena.adapters.exchanges.binance import Binance
from elena.exchange_manager import ExchangeManager
from elena.ports import exchange
from elena.record import Record

test_data_dir = Path.joinpath(Path(__file__).parent.parent, 'test_data')


def load_test_data(filename: str) -> dict:
    file_path = Path.joinpath(test_data_dir, filename)
    with open(file_path) as json_file:
        data = json.load(json_file)
    return data


# Record test data for method get_candles
# Remove the '_' to run on tests
def _test_record_get_candles_for_binance():
    exchange = Binance()
    sut = ExchangeManager(exchange)
    Record.enable()
    sut.get_candles(p_symbol='ETHBUSD', p_interval=Client.KLINE_INTERVAL_1MINUTE, p_limit=10)


# Test method get_candles with get_klines mock based on previously recorded data
def test_get_candles():
    Record.disable()

    get_klines_data = load_test_data('1645107155828-1645107156451-get_klines.json')
    exchange_mock = mock(spec=exchange.Exchange)
    when(exchange_mock).get_klines(
        get_klines_data['input']['p_interval'],
        get_klines_data['input']['p_limit'],
        get_klines_data['input']['p_symbol'],
    ).thenReturn(get_klines_data['output'])

    get_candles_data = load_test_data('1645107155828-1645107156453-get_candles.json')
    sut = ExchangeManager(exchange_mock)
    actual = sut.get_candles(
        p_symbol=get_candles_data['input']['p_symbol'],
        p_interval=get_candles_data['input']['p_interval'],
        p_limit=get_candles_data['input']['p_limit'],
    )

    assert actual.to_json() == get_candles_data['output']
