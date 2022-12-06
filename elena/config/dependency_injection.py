from typing import Dict

from dependency_injector import containers, providers

from elena.adapters.bot_manager.local_bot_manager import LocalBotManager
from elena.adapters.logger.local_logger import LocalLogger
from elena.adapters.market_reader.cctx_market_reader import CctxMarketReader
from elena.adapters.order_writer.cctx_order_writer import CctxOrderWriter
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
        CctxMarketReader,
        config=config,
        logger=logger
    )
    order_writer = providers.Singleton(
        CctxOrderWriter,
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
