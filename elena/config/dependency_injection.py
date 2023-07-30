from typing import Dict

from dependency_injector import containers, providers

from elena.adapters.bot_manager.local_bot_manager import LocalBotManager
from elena.adapters.exchange_manager.cctx_exchange_manager import CctxExchangeManager
from elena.adapters.logger.local_logger import LocalLogger
from elena.domain.services.elena import Elena


def get_container(config: Dict) -> containers.DynamicContainer:
    container = containers.DynamicContainer()

    logger = providers.Singleton(
        LocalLogger, config=config
    )
    container.logger = logger
    bot_manager = providers.Singleton(
        LocalBotManager,
        config=config,
        logger=logger
    )
    exchange_manager = providers.Singleton(
        CctxExchangeManager,
        config=config,
        logger=logger
    )
    container.elena = providers.Singleton(
        Elena,
        config=config,
        logger=logger,
        bot_manager=bot_manager,
        exchange_manager=exchange_manager
    )
    return container
