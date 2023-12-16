from typing import Protocol

from elena.domain.ports.logger import Logger


class MetricsManager(Protocol):
    def init(self, config: dict, logger: Logger):
        ...

    def counter(self, name, value, **kwargs):
        ...

    def histogram(self, name, value, **kwargs):
        ...
