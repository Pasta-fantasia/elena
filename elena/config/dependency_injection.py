from typing import Dict

from dependency_injector import containers, providers

from elena.adapters.bot_manager.local_bot_manager import LocalBotManager
from elena.adapters.exchange_reader.cctx_exchange_reader import CctxExchangeReader
from elena.adapters.logger.local_logger import LocalLogger
from elena.adapters.order_manager.cctx_order_manager import CctxOrderManager
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
    exchange_reader = providers.Singleton(
        CctxExchangeReader,
        config=config,
        logger=logger
    )
    order_manager = providers.Singleton(
        CctxOrderManager,
        config=config,
        logger=logger
    )
    container.elena = providers.Singleton(
        Elena,
        config=config,
        logger=logger,
        bot_manager=bot_manager,
        exchange_reader=exchange_reader,
        order_manager=order_manager
    )
    return container
