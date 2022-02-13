import json

from elena.utils import get_time


class TestDataRecorder:
    def __init__(self, file_prefix, path='../test_data'):
        self._file_prefix = file_prefix
        self._path = path
        self._filename = None
        self._current_record = {}
        self._recording = False

    def start(self):
        self._filename = f'{self._path}/{self._file_prefix}-{get_time()}.json'
        self._current_record = {}
        self._recording = True

    def func_in(self, function: str, **kargs):
        if not self._recording:
            return
        if function in self._current_record:
            raise RuntimeError(f'function {function} already exists')
        self._current_record[function] = {}
        self._current_record[function]['input'] = kargs

    def call_in(self, function: str, call: str, **kargs):
        if not self._recording:
            return
        if not function in self._current_record:
            raise RuntimeError(f'function {function} does not exists')
        if call in self._current_record[function]:
            raise RuntimeError(f'call input {call} for function {function} already exists')
        d = {'input': kargs}
        self._current_record[function][call] = d

    def call_out(self, function: str, call: str, **kargs):
        if not self._recording:
            return
        if not function in self._current_record:
            raise RuntimeError(f'function {function} does not exists')
        if not call in self._current_record[function]:
            raise RuntimeError(f'call {call} for function {function} does not exists')
        d = self._current_record[function][call]
        if 'output' in d:
            raise RuntimeError(f'call output {call} for function {function} already exists')
        d['output'] = kargs
        self._current_record[function][call] = d

    def func_out(self, function: str, **kargs):
        if not self._recording:
            return
        if not function in self._current_record:
            raise RuntimeError(f'function {function} does not exists')
        if 'output' in self._current_record[function]:
            raise RuntimeError(f'function {function} already exists')
        self._current_record[function]['output'] = kargs

    def stop(self):
        if not self._recording:
            return
        self._recording = False
        fp = open(self._filename, 'w')
        json.dump(self._current_record, fp, indent=4)
        fp.close()
        self._current_record = {}