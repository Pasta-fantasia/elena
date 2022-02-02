import json
import time


# General functions

def get_time():
    return int(time.time() * 1000)


class TestDataRecorder:
    def __init__(self, file_prefix, path='../test_data'):
        self._file_prefix = file_prefix
        self._path = path
        self._filename = None
        self._current_record = {}

    def start(self):
        self._filename = f'{self._path}/{self._file_prefix}-{get_time()}.json'
        self._current_record = {}

    def method_input(self, method: str, **kargs):
        if method in self._current_record:
            raise RuntimeError(f'method {method} already exists')
        self._current_record[method] = {}
        self._current_record[method]['input'] = kargs

    def call_input(self, method: str, call: str, **kargs):
        if not method in self._current_record:
            raise RuntimeError(f'method {method} does not exists')
        if call in self._current_record[method]:
            raise RuntimeError(f'call input {call} for method {method} already exists')
        d = {'input': kargs}
        self._current_record[method][call] = d

    def call_output(self, method: str, call: str, **kargs):
        if not method in self._current_record:
            raise RuntimeError(f'method {method} does not exists')
        if not call in self._current_record[method]:
            raise RuntimeError(f'call {call} for method {method} does not exists')
        d = self._current_record[method][call]
        if 'output' in d:
            raise RuntimeError(f'call output {call} for method {method} already exists')
        d['output'] = kargs
        self._current_record[method][call] = d

    def method_output(self, method: str, **kargs):
        if not method in self._current_record:
            raise RuntimeError(f'method {method} does not exists')
        if 'output' in self._current_record[method]:
            raise RuntimeError(f'method {method} already exists')
        self._current_record[method]['output'] = kargs

    def stop(self):
        fp = open(self._filename, 'w')
        json.dump(self._current_record, fp, indent=4)
        fp.close()
        self._current_record = {}
