import logging
import time
from datetime import datetime

from elena.domain.ports.config import Config
from elena.domain.ports.emit_flesti import EmitFlesti


class AsapEmitFlesti(EmitFlesti):

    def __init__(self, config: Config, start_iso_datetime: str = None):
        super().__init__(config)
        self._period = self._load_period(config)
        self._start = self._load_start(start_iso_datetime)
        self._disabled = True

    def _load_start(self, start_iso_datetime):
        if start_iso_datetime:
            try:
                return datetime.fromisoformat(start_iso_datetime).timestamp()
            except ValueError:
                raise RuntimeError(
                    f"Wrong configuration value 'EmitFlesti.start_iso_datetime': {start_iso_datetime} is not a valid ISO datetime")
        else:
            self._start = None

    def now(self) -> float:
        return self._start

    def __iter__(self):
        if not self._start:
            self._start = time.time()
        logging.info('Starting ASAP emit flesti with %s minutes period starting at %s', self._period.value,
                     time.asctime(time.localtime(self._start)))
        return self

    def __next__(self) -> float:
        if self._disabled:
            self._disabled = False

        self._start = self._start + self._period.value * 60
        return self._start
