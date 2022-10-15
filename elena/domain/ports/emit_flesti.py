from typing import Protocol

from elena.domain.model.time_period import TimePeriod
from elena.domain.ports.config import Config


class EmitFlesti(Protocol):

    def __init__(self, config: Config):
        pass

    @staticmethod
    def _load_period(config: Config):
        _period = config.get('EmitFlesti', 'period_minutes')
        try:
            return TimePeriod(_period)
        except ValueError:
            raise RuntimeError(
                f"Wrong configuration value 'EmitFlesti.period': {_period} is not a valid TimePeriod")

    def now(self) -> float:
        pass

    def __iter__(self):
        pass

    def __next__(self) -> float:
        pass
