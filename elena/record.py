import json
import pandas as pd
from elena.utils import get_time


def record(func):
    def wrapper(*args, **kwargs):
        _time = get_time()
        _output = func(*args, **kwargs)
        if isinstance(_output, pd.DataFrame):
            __output = _output.to_json()
        else:
            __output = _output
        _record = {
            'time': _time,
            'function': f'{func.__name__}',
            'input': kwargs,  ## TODO convert args tuple to dict and add it to input.args entry
            'output': __output,
        }
        _fp = open(f'../test_data/{_time}-{func.__name__}.json', 'a')
        json.dump(_record, _fp, indent=4)
        _fp.close()
        return _output

    return wrapper
