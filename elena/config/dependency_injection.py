import logging
import pathlib
import sys
from os import path

from elena.adapters.bot_status_manager.local_bot_status_manager import LocalBotStatusManager
from elena.adapters.config.local_config import LocalConfig
from elena.adapters.market_reader.kucoin_market_reader import KuCoinMarketReader
from elena.adapters.order_writer.kucoin_order_writer import KuCoinOrderWriter
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


def get_service(profile: str, home: str) -> elena.Elena:
    func_mapper = {"local": _local, "prod": _prod}
    return func_mapper[profile](home)


def _local(home: str) -> elena.Elena:
    _init_logging(logging.DEBUG)
    _config = LocalConfig(home)
    _bot_status_manager = LocalBotStatusManager()
    _market_reader = KuCoinMarketReader()
    _order_writer = KuCoinOrderWriter()

    logging.info("Completed Elena dependency injection with test profile")
    _elena = elena.Elena(_config, _bot_status_manager, _market_reader, _order_writer)
    return _elena


def _prod(home: str) -> elena.Elena:
    _init_logging(logging.INFO)
    _config = LocalConfig(home)
    _bot_status_manager = LocalBotStatusManager()
    _market_reader = KuCoinMarketReader()
    _order_writer = KuCoinOrderWriter()

    logging.info("Completed Elena dependency injection with production profile")
    _elena = elena.Elena(_config, _bot_status_manager, _market_reader, _order_writer)
    return _elena
