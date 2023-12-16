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
        level = logging.getLevelName(config["LocalLogger"]["level"])
        file_path = path.join(config["home"], config["LocalLogger"]["path"])
        Path(file_path).mkdir(parents=True, exist_ok=True)
        file = path.join(pathlib.Path(file_path), "elena.log")
        logging.basicConfig(
            level=level,
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers=[
                logging.handlers.RotatingFileHandler(
                    file,
                    maxBytes=config["LocalLogger"]["max_bytes"],
                    backupCount=config["LocalLogger"]["backup_count"],
                ),
                logging.StreamHandler(sys.stdout),
            ],
        )
        print(f"Logging {config['LocalLogger']['level']} level to file `{file}`")

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
