import logging
import pathlib
import sys
from os import path
from pathlib import Path
from typing import Dict

from elena.domain.ports.logger import Logger


class LocalLogger(Logger):

    def __init__(self, config: Dict):
        _level = logging.getLevelName(config['LocalLogger']['level'])
        _path = pathlib.Path(config['LocalLogger']['path'])
        Path(_path).mkdir(parents=True, exist_ok=True)
        _file = path.join(pathlib.Path(_path), 'elena.log')
        logging.basicConfig(
            level=_level,
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers=[
                logging.FileHandler(_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        print(f"Logging {config['LocalLogger']['level']} level to file `{_file}`")

    @staticmethod
    def critical(msg, *args, **kwargs):
        logging.critical(msg, *args, **kwargs)

    @staticmethod
    def error(msg, *args, **kwargs):
        logging.error(msg, *args, **kwargs)

    @staticmethod
    def exception(msg, *args, exc_info=True, **kwargs):
        logging.exception(msg, *args, exc_info=exc_info, **kwargs)

    @staticmethod
    def warning(msg, *args, **kwargs):
        logging.warning(msg, *args, **kwargs)

    @staticmethod
    def info(msg, *args, **kwargs):
        logging.info(msg, *args, **kwargs)

    @staticmethod
    def debug(msg, *args, **kwargs):
        logging.debug(msg, *args, **kwargs)
