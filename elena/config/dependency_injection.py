from elena.adapters.bot_status_manager.local_bot_status_manager import LocalBotSpawner
from elena.adapters.config.local_config import LocalConfig
from elena.adapters.logger.local_logger import LocalLogger
from elena.adapters.market_reader.kucoin_market_reader import KuCoinMarketReader
from elena.adapters.order_writer.kucoin_order_writer import KuCoinOrderWriter
from elena.domain.services import elena


def get_service(profile: str, home: str) -> elena.Elena:
    func_mapper = {"local": _local, "prod": _prod}
    return func_mapper[profile](home)


def _local(home: str) -> elena.Elena:
    _config = LocalConfig(home)
    _logger = LocalLogger(_config)
    _bot_spawner = LocalBotSpawner(_config, _logger)
    _market_reader = KuCoinMarketReader(_config, _logger)
    _order_writer = KuCoinOrderWriter(_config, _logger)

    _logger.info("Completed Elena dependency injection with test profile")
    _elena = elena.Elena(_config, _logger, _bot_spawner, _market_reader, _order_writer)
    return _elena


def _prod(home: str) -> elena.Elena:
    _config = LocalConfig(home)
    _logger = LocalLogger(_config)
    _bot_spawner = LocalBotSpawner(_config, _logger)
    _market_reader = KuCoinMarketReader(_config, _logger)
    _order_writer = KuCoinOrderWriter(_config, _logger)

    _logger.info("Completed Elena dependency injection with production profile")
    _elena = elena.Elena(_config, _logger, _bot_spawner, _market_reader, _order_writer)
    return _elena
