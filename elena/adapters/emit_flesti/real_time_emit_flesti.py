import logging
import time

from elena.domain.model.time_period import TimePeriod
from elena.domain.ports.config import Config
from elena.domain.ports.emit_flesti import EmitFlesti


class RealTimeEmitFlesti(EmitFlesti):

    def __init__(self, config: Config):
        super().__init__(config)
        self._period = TimePeriod(config.get('EmitFlesti', 'period'))
        self._start = None

    def now(self) -> float:
        return time.time()

    def __iter__(self):
        self._start = time.time()
        logging.info('Starting real time emit flesti with %s minutes period', self._period.value)
        return self

    def __next__(self) -> float:
        _elapsed = time.time() - self._start
        if self._period > _elapsed:
            _wait = self._period.value * 60 - _elapsed
            time.sleep(_wait)
        else:
            logging.warning('Configured period %d is too low for current work cycle duration %f', self._period, _elapsed)
        self._start = time.time()
        return self._start
