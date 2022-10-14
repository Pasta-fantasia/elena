from typing import Protocol

from elena.domain.model.time_period import TimePeriod
from elena.domain.ports.config import Config


class EmitFlesti(Protocol):

    def __init__(self, config: Config):
        pass

    @staticmethod
    def _load_period(config: Config):
        try:
            return TimePeriod(config.get('EmitFlesti', 'period'))
        except ValueError:
            raise RuntimeError(
                f"Wrong configuration value 'EmitFlesti.period': {config.get('EmitFlesti', 'period')} is not a valid TimePeriod")

    def now(self) -> float:
        pass

    def __iter__(self):
        pass

    def __next__(self) -> float:
        pass
