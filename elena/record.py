import json
import pandas as pd

from config.record_config import record
from elena.utils import get_time


class Record:
    def __call__(self, func):
        def wrapper(*args, **kwargs):
            _output = func(*args, **kwargs)
            if self._is_enabled(func.__name__):
                self._record(kwargs, _output, func.__name__)
            return _output

        return wrapper

    @staticmethod
    def _is_enabled(function_name) -> bool:
        # TODO consider a better approach
        if record['enabled'] and function_name in record['functions']:
            return record['functions'][function_name]
        return False

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
