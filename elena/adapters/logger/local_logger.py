import logging
import logging.handlers
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
                logging.handlers.RotatingFileHandler(
                    _file,
                    maxBytes=config['LocalLogger']['max_bytes'],
                    backupCount=config['LocalLogger']['backup_count']
                ),
                logging.StreamHandler(sys.stdout)
            ]
        )
        print(f"Logging {config['LocalLogger']['level']} level to file `{_file}`")

    def critical(self, msg, *args, **kwargs):
        logging.critical(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        logging.error(msg, *args, **kwargs)

    def exception(self, msg, *args, exc_info=True, **kwargs):
        logging.exception(msg, *args, exc_info=exc_info, **kwargs)

    def warning(self, msg, *args, **kwargs):
        logging.warning(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        logging.info(msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        logging.debug(msg, *args, **kwargs)
