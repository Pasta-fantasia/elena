import logging
import pathlib
import sys
from os import path

from elena.adapters.config.local_config import LocalConfig
from elena.domain.services import elena


def _init_logging(level):
    _file = path.join(pathlib.Path(__file__).parent.parent.parent.parent.absolute(), 'elena.log')
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(_file),
            logging.StreamHandler(sys.stdout)
        ]
    )


def get_service(profile: str) -> elena.Elena:
    func_mapper = {"dev": _dev, "test": _test, "prod": _prod}
    return func_mapper[profile]()


def _dev() -> elena.Elena:
    _init_logging(logging.DEBUG)
    _config = LocalConfig('dev')

    logging.info("Completed Elena dependency injection with development profile")
    _elena = elena.Elena(_config)
    return _elena


def _test() -> elena.Elena:
    _init_logging(logging.DEBUG)
    _config = LocalConfig('dev')

    logging.info("Completed Elena dependency injection with test profile")
    _elena = elena.Elena(_config)
    return _elena


def _prod() -> elena.Elena:
    _init_logging(logging.INFO)
    _config = LocalConfig('dev')

    logging.info("Completed Elena dependency injection with production profile")
    _elena = elena.Elena(_config)
    return _elena
