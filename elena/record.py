import json
import pandas as pd
from elena.utils import get_time


class Record:
    def __init__(self, enable_recording):
        self._enabled = enable_recording

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            _output = func(*args, **kwargs)
            if self._enabled:
                self._record(kwargs, _output, func.__name__)
            return _output

        return wrapper

    def _record(self, kwargs, output, function_name):
        _time = get_time()
        _data = {
            'time': _time,
            'function': function_name,
            'input': kwargs,  ## TODO convert args tuple to dict and add it to input.args entry
            'output': self._serialize_output(output),
        }
        self._save(_data, _time, function_name)

    @staticmethod
    def _serialize_output(output):
        if isinstance(output, pd.DataFrame):
            return output.to_json()
        return output

    @staticmethod
    def _save(data, time, function):
        _fp = open(f'../test_data/{time}-{function}.json', 'w')
        json.dump(data, _fp, indent=4)
        _fp.close()
