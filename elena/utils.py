import json
import time


# General functions

def get_time():
    return int(time.time() * 1000)


class TestDataRecorder:
    def __init__(self):
        self._filename = None
        self._current_record = {}

    def start(self):
        self._filename = f'../test_data/{get_time()}.json'
        self._current_record = {}

    def method_input(self, method: str, **kargs):
        self._current_record[method] = {}
        self._current_record[method]['input'] = kargs

    def call_input(self, method: str, call: str, **kargs):
        if not method in self._current_record:
            raise RuntimeError(f'method {method} does not exists')
        if not call in self._current_record[method]:
            self._current_record[method][call] = []
        d = {'input': kargs}
        self._current_record[method][call] = d

    def call_output(self, method: str, call: str, **kargs):
        if not method in self._current_record:
            raise RuntimeError(f'method {method} does not exists')
        if not call in self._current_record[method]:
            raise RuntimeError(f'call {call} does not exists')
        d = self._current_record[method][call]
        d['output'] = kargs
        self._current_record[method][call] = d


    def method_output(self, method: str, **kargs):
        if not method in self._current_record:
            raise RuntimeError(f'method {method} does not exists')
        self._current_record[method]['output'] = kargs

    def stop(self):
        fp = open(self._filename, 'w')
        json.dump(self._current_record, fp)
        fp.close()
        self._current_record = {}
