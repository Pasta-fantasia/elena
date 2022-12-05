from dependency_injector import containers, providers

from elena.adapters.bot_status_manager.local_bot_status_manager import LocalBotSpawner
from elena.adapters.config.local_config import LocalConfig
from elena.adapters.logger.local_logger import LocalLogger
from elena.adapters.market_reader.kucoin_market_reader import KuCoinMarketReader
from elena.adapters.order_writer.kucoin_order_writer import KuCoinOrderWriter
from elena.domain.services.elena import Elena


class Container(containers.DeclarativeContainer):
    config = providers.Factory(LocalConfig)
    logger = providers.Factory(LocalLogger, config=config)
    bot_spawner = providers.Factory(LocalBotSpawner, config=config, logger=logger)
    market_reader = providers.Factory(KuCoinMarketReader, config=config, logger=logger)
    order_writer = providers.Factory(KuCoinOrderWriter, config=config, logger=logger)
    elena = providers.Factory(
        Elena,
        config=config,
        logger=logger,
        bot_spawner=bot_spawner,
        market_reader=market_reader,
        order_writer=order_writer
    )


