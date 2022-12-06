from typing import Dict

from dependency_injector import containers, providers

from elena.adapters.bot_status_manager.local_bot_manager import LocalBotManager
from elena.adapters.logger.local_logger import LocalLogger
from elena.adapters.market_reader.kucoin_market_reader import KuCoinMarketReader
from elena.adapters.order_writer.kucoin_order_writer import KuCoinOrderWriter
from elena.domain.services.elena import Elena


def get_container(config: Dict) -> containers.DynamicContainer:
    container = containers.DynamicContainer()

    logger = providers.Singleton(
        LocalLogger, config=config
    )
    bot_manager = providers.Singleton(
        LocalBotManager,
        config=config,
        logger=logger
    )
    market_reader = providers.Singleton(
        KuCoinMarketReader,
        config=config,
        logger=logger
    )
    order_writer = providers.Singleton(
        KuCoinOrderWriter,
        config=config,
        logger=logger
    )
    container.elena = providers.Singleton(
        Elena,
        config=config,
        logger=logger,
        bot_manager=bot_manager,
        market_reader=market_reader,
        order_writer=order_writer
    )
    return container
