import json
import pandas as pd
from elena.utils import get_time


def record(func):
    def wrapper(*args, **kwargs):
        _time = get_time()
        _function = func.__name__
        _output = func(*args, **kwargs)
        _data = {
            'time': _time,
            'function': _function,
            'input': kwargs,  ## TODO convert args tuple to dict and add it to input.args entry
            'output': _serialize_output(_output),
        }
        _save(_data, _time, _function)
        return _output

    return wrapper


def _serialize_output(output):
    if isinstance(output, pd.DataFrame):
        return output.to_json()
    return output


def _save(data, time, function):
    _fp = open(f'../test_data/{time}-{function}.json', 'w')
    json.dump(data, _fp, indent=4)
    _fp.close()
