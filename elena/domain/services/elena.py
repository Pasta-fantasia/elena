import logging
import time

from elena.domain.ports.config import Config
from elena.domain.ports.emit_flesti import EmitFlesti


class Elena:

    def __init__(self, config: Config, emit_flesti: EmitFlesti):
        self._config = config
        self._emit_flesti = emit_flesti
        logging.info('Elena initialized')

    def run(self):
        _profile = self._config.get('Common', 'profile')
        logging.info(f'Starting Elena on {_profile} profile.')

        for start_time in self._emit_flesti:
            self._run_cycle(start_time)

    def _run_cycle(self, start_time: float):
        logging.info(f'Starting cycle at %s (%f)', time.asctime(time.localtime(start_time)), start_time)
        time.sleep(0.6)
