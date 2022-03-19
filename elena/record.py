import json
import pandas as pd

from elena.utils import get_time


class Record:
    prefix: int = 0

    @staticmethod
    def enable():
        Record.prefix = get_time()

    @staticmethod
    def disable():
        Record.prefix = 0

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            _output = func(*args, **kwargs)
            if self._is_enabled():
                self._record(kwargs, _output, func.__name__)
            return _output

        return wrapper

    def _is_enabled(self) -> bool:
        return self.prefix > 0

    def _record(self, kwargs, output, function_name):
        _time = get_time()
        _data = {
            'time': _time,
            'function': function_name,
            'input': kwargs,
            'output': self._serialize_output(output),
        }
        self._save(_data, _time, function_name)

    @staticmethod
    def _serialize_output(output):
        if isinstance(output, pd.DataFrame):
            return output.to_json()
        return output

    def _save(self, data, time, function):
        _fp = open(f'../test_data/{self.prefix}-{time}-{function}.json', 'w')
        json.dump(data, _fp, indent=4)
        _fp.close()
