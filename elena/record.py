import json
import pandas as pd
from elena.utils import get_time


def record(func):
    def wrapper(*args, **kwargs):
        _output = func(*args, **kwargs)
        _time = get_time()
        if isinstance(_output, pd.DataFrame):
            _output = _output.to_json()
        _record = {
            'time': _time,
            'function': f'{func.__name__}',
            'input': kwargs,  ## TODO convert args tuple to dict and add it to input.args entry
            'output': _output,
        }
        fp = open(f'../test_data/{_time}-{func.__name__}.json', 'a')
        json.dump(_record, fp, indent=4)
        fp.close()
        return _output

    return wrapper
