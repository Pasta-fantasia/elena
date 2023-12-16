from typing import Protocol


class Logger(Protocol):
    def init(self, config: dict):
        ...

    def critical(self, msg, *args, **kwargs):
        ...

    def error(self, msg, *args, **kwargs):
        ...

    def exception(self, msg, *args, exc_info=True, **kwargs):
        ...

    def warning(self, msg, *args, **kwargs):
        ...

    def info(self, msg, *args, **kwargs):
        ...

    def debug(self, msg, *args, **kwargs):
        ...
