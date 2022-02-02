import json
import time

from _pytest.python_api import raises
from mockito import when

from elena.utils import TestDataRecorder, get_time

df_dict = {
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
    sut = TestDataRecorder('test_utils')
    sut.start()
    sut.method_input('get_candles', p_symbol='ETHBUSD', p_interval='1m', p_limit=1000)

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
    sut = TestDataRecorder('test_utils')
    sut.start()
    sut.method_input('get_candles', p_symbol='ETHBUSD', p_interval='1m', p_limit=1000)
    with raises(RuntimeError) as err:
        sut.method_input('get_candles', p_symbol='ETHBUSD', p_interval='1m', p_limit=1000)
    assert err.value.args[0] == 'method get_candles already exists'


def test_call_input():
    sut = TestDataRecorder('test_utils')
    sut.start()
    sut.method_input('get_candles', p_symbol='ETHBUSD', p_interval='1m', p_limit=1000)
    sut.call_input('get_candles', '_api.get_klines', p_symbol='ETHBUSD', p_interval='1m', p_limit=1000)

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
    sut = TestDataRecorder('test_utils')
    sut.start()

    with raises(RuntimeError) as err:
        sut.call_input('get_candles', '_api.get_klines', p_symbol='ETHBUSD', p_interval='1m', p_limit=1000)
    assert err.value.args[0] == 'method get_candles does not exists'


def test_call_input_duplicated_call():
    sut = TestDataRecorder('test_utils')
    sut.start()
    sut.method_input('get_candles', p_symbol='ETHBUSD', p_interval='1m', p_limit=1000)
    sut.call_input('get_candles', '_api.get_klines', p_symbol='ETHBUSD', p_interval='1m', p_limit=1000)
    with raises(RuntimeError) as err:
        sut.call_input('get_candles', '_api.get_klines', p_symbol='ETHBUSD', p_interval='1m', p_limit=1000)
    assert err.value.args[0] == 'call input _api.get_klines for method get_candles already exists'


def test_call_output():
    sut = TestDataRecorder('test_utils')
    sut.start()
    sut.method_input('get_candles', p_symbol='ETHBUSD', p_interval='1m', p_limit=1000)
    sut.call_input('get_candles', '_api.get_klines', p_symbol='ETHBUSD', p_interval='1m', p_limit=1000)
    sut.call_output('get_candles', '_api.get_klines', klines=df_dict)

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
                    'klines': df_dict,
                }
            },
        },
    }


def test_call_output_method_does_not_exists():
    sut = TestDataRecorder('test_utils')
    sut.start()

    with raises(RuntimeError) as err:
        sut.call_output('get_candles', '_api.get_klines', klines=df_dict)
    assert err.value.args[0] == 'method get_candles does not exists'


def test_call_output_call_does_not_exists():
    sut = TestDataRecorder('test_utils')
    sut.start()
    sut.method_input('get_candles', p_symbol='ETHBUSD', p_interval='1m', p_limit=1000)

    with raises(RuntimeError) as err:
        sut.call_output('get_candles', '_api.get_klines', klines=df_dict)
    assert err.value.args[0] == 'call _api.get_klines for method get_candles does not exists'


# noinspection DuplicatedCode
def test_call_output_duplicated_call():
    sut = TestDataRecorder('test_utils')
    sut.start()
    sut.method_input('get_candles', p_symbol='ETHBUSD', p_interval='1m', p_limit=1000)
    sut.call_input('get_candles', '_api.get_klines', p_symbol='ETHBUSD', p_interval='1m', p_limit=1000)
    sut.call_output('get_candles', '_api.get_klines', klines=df_dict)

    with raises(RuntimeError) as err:
        sut.call_output('get_candles', '_api.get_klines', klines=df_dict)
    assert err.value.args[0] == 'call output _api.get_klines for method get_candles already exists'


# noinspection DuplicatedCode
def test_method_output():
    sut = TestDataRecorder('test_utils')
    sut.start()
    sut.method_input('get_candles', p_symbol='ETHBUSD', p_interval='1m', p_limit=1000)
    sut.call_input('get_candles', '_api.get_klines', p_symbol='ETHBUSD', p_interval='1m', p_limit=1000)
    sut.call_output('get_candles', '_api.get_klines', klines=df_dict)
    sut.method_output('get_candles', candles_df=df_dict)

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
                    'klines': df_dict,
                }
            },
            'output': {
                'candles_df': df_dict
            }
        },
    }


# noinspection DuplicatedCode
def test_method_output_duplicated_call():
    sut = TestDataRecorder('test_utils')
    sut.start()
    sut.method_input('get_candles', p_symbol='ETHBUSD', p_interval='1m', p_limit=1000)
    sut.call_input('get_candles', '_api.get_klines', p_symbol='ETHBUSD', p_interval='1m', p_limit=1000)
    sut.call_output('get_candles', '_api.get_klines', klines=df_dict)
    sut.method_output('get_candles', candles_df=df_dict)

    with raises(RuntimeError) as err:
        sut.method_output('get_candles', candles_df=df_dict)
    assert err.value.args[0] == 'method get_candles already exists'


# noinspection DuplicatedCode
def test_stop():
    when(time).time().thenReturn(1)

    sut = TestDataRecorder('test_utils', '.')
    sut.start()
    sut.method_input('get_candles', p_symbol='ETHBUSD', p_interval='1m', p_limit=1000)
    sut.call_input('get_candles', '_api.get_klines', p_symbol='ETHBUSD', p_interval='1m', p_limit=1000)
    sut.call_output('get_candles', '_api.get_klines', klines="FAKE KLINES")
    sut.method_output('get_candles', candles_df="FAKE KLINES")
    sut.stop()

    expected = {
        "get_candles": {
            "input": {
                "p_symbol": "ETHBUSD",
                "p_interval": "1m",
                "p_limit": 1000
            },
            "_api.get_klines": {
                "input": {
                    "p_symbol": "ETHBUSD",
                    "p_interval": "1m",
                    "p_limit": 1000
                },
                "output": {
                    "klines": "FAKE KLINES"
                }
            },
            "output": {
                "candles_df": "FAKE KLINES"
            }
        }
    }

    with open('./test_utils-1000.json') as f:
        actual = json.load(f)

    assert actual == expected
