import logging
import pathlib
import sys
from os import path

from elena.adapters.bot_status_manager.local_bot_status_manager import LocalBotStatusManager
from elena.adapters.config.local_config import LocalConfig
from elena.adapters.emit_flesti.asap_emit_flesti import AsapEmitFlesti
from elena.adapters.emit_flesti.real_time_emit_flesti import RealTimeEmitFlesti
from elena.adapters.market_reader.kucoin_market_reader import KuCoinMarketReader
from elena.adapters.order_writer.kucoin_order_writer import KuCoinOrderWriter
from elena.adapters.summary_writer.local_summary_writer import LocalSummaryWriter
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
    _emit_flesti = AsapEmitFlesti(_config)
    _bot_status_manager = LocalBotStatusManager(_emit_flesti)
    _summary_writer = LocalSummaryWriter()
    _market_reader = KuCoinMarketReader(_emit_flesti)
    _order_writer = KuCoinOrderWriter(_emit_flesti)

    logging.info("Completed Elena dependency injection with development profile")
    _elena = elena.Elena(_config, _emit_flesti, _bot_status_manager, _summary_writer, _market_reader, _order_writer)
    return _elena


def _test() -> elena.Elena:
    _init_logging(logging.DEBUG)
    _config = LocalConfig('test')
    _emit_flesti = AsapEmitFlesti(_config)
    _bot_status_manager = LocalBotStatusManager(_emit_flesti)
    _summary_writer = LocalSummaryWriter()
    _market_reader = KuCoinMarketReader(_emit_flesti)
    _order_writer = KuCoinOrderWriter(_emit_flesti)

    logging.info("Completed Elena dependency injection with test profile")
    _elena = elena.Elena(_config, _emit_flesti, _bot_status_manager, _summary_writer, _market_reader, _order_writer)
    return _elena


def _prod() -> elena.Elena:
    _init_logging(logging.DEBUG)
    _config = LocalConfig('prod')
    _emit_flesti = RealTimeEmitFlesti(_config)
    _bot_status_manager = LocalBotStatusManager(_emit_flesti)
    _summary_writer = LocalSummaryWriter()
    _market_reader = KuCoinMarketReader(_emit_flesti)
    _order_writer = KuCoinOrderWriter(_emit_flesti)

    logging.info("Completed Elena dependency injection with production profile")
    _elena = elena.Elena(_config, _emit_flesti, _bot_status_manager, _summary_writer, _market_reader, _order_writer)
    return _elena
