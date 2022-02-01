from binance import Client
from _pytest.python_api import raises
from elena.utils import TestDataRecorder, get_time

df = {
    'Open time': [get_time()],
    'Open': [get_time()],
    'High': [get_time()],
    'Low': [get_time()],
    'Close': [get_time()],
    'Volume': [get_time()],
    'Close time': [get_time()],
    'Quote asset volume': [12345],
    'Number of trades': [33],
    'Taker buy base asset volume': [123.45],
    'Taker buy quote asset volume': [133.45],
    'Ignore': [''],
}


def test_method_input():
    sut = TestDataRecorder()
    sut.start()
    sut.method_input('get_candles', p_symbol='ETHBUSD', p_interval=Client.KLINE_INTERVAL_1MINUTE, p_limit=1000)

    actual = sut._current_record

    assert actual == {
        'get_candles': {
            'input': {
                'p_interval': '1m',
                'p_limit': 1000,
                'p_symbol': 'ETHBUSD',
            }
        },
    }


def test_call_input_duplicated_method():
    raise AssertionError('Not implemented')


def test_call_input():
    sut = TestDataRecorder()
    sut.start()
    sut.method_input('get_candles', p_symbol='ETHBUSD', p_interval=Client.KLINE_INTERVAL_1MINUTE, p_limit=1000)
    sut.call_input('get_candles', '_api.get_klines', p_symbol='ETHBUSD', p_interval=Client.KLINE_INTERVAL_1MINUTE,
                   p_limit=1000)

    actual = sut._current_record

    assert actual == {
        'get_candles': {
            'input': {
                'p_interval': '1m',
                'p_limit': 1000,
                'p_symbol': 'ETHBUSD',
            },
            '_api.get_klines': {
                'input': {
                    'p_interval': '1m',
                    'p_limit': 1000,
                    'p_symbol': 'ETHBUSD',
                },
            },
        },
    }


def test_call_input_method_does_not_exists():
    sut = TestDataRecorder()
    sut.start()

    with raises(RuntimeError) as err:
        sut.call_input('get_candles', '_api.get_klines', p_symbol='ETHBUSD', p_interval=Client.KLINE_INTERVAL_1MINUTE,
                       p_limit=1000)
    assert err.value.args[0] == 'method get_candles does not exists'


def test_call_input_duplicated_call():
    raise AssertionError('Not implemented')


def test_call_output():
    sut = TestDataRecorder()
    sut.start()
    sut.method_input('get_candles', p_symbol='ETHBUSD', p_interval=Client.KLINE_INTERVAL_1MINUTE, p_limit=1000)
    sut.call_input('get_candles', '_api.get_klines', p_symbol='ETHBUSD', p_interval=Client.KLINE_INTERVAL_1MINUTE,
                   p_limit=1000)
    sut.call_output('get_candles', '_api.get_klines', klines=df)

    actual = sut._current_record

    assert actual == {
        'get_candles': {
            'input': {
                'p_interval': '1m',
                'p_limit': 1000,
                'p_symbol': 'ETHBUSD',
            },
            '_api.get_klines': {
                'input': {
                    'p_interval': '1m',
                    'p_limit': 1000,
                    'p_symbol': 'ETHBUSD',
                },
                'output': {
                    'klines': df,
                }
            },
        },
    }


def test_method_output():
    sut = TestDataRecorder()
    sut.start()
    sut.method_input('get_candles', p_symbol='ETHBUSD', p_interval=Client.KLINE_INTERVAL_1MINUTE, p_limit=1000)
    sut.call_input('get_candles', '_api.get_klines', p_symbol='ETHBUSD', p_interval=Client.KLINE_INTERVAL_1MINUTE,
                   p_limit=1000)
    sut.call_output('get_candles', '_api.get_klines', klines=df)
    sut.method_output('get_candles', candles_df=df)

    actual = sut._current_record

    assert actual == {
        'get_candles': {
            'input': {
                'p_interval': '1m',
                'p_limit': 1000,
                'p_symbol': 'ETHBUSD',
            },
            '_api.get_klines': {
                'input': {
                    'p_interval': '1m',
                    'p_limit': 1000,
                    'p_symbol': 'ETHBUSD',
                },
                'output': {
                    'klines': df,
                }
            },
            'output': {
                'candles_df': df
            }
        },
    }


def test_call_stop():
    raise AssertionError('Not implemented')
# TODO Mock writing file
