from typing import Optional

from elena.adapters.bot_manager.local_bot_manager import LocalBotManager
from elena.adapters.config.local_config_reader import LocalConfigReader
from elena.adapters.exchange_manager.cctx_exchange_manager import \
    CctxExchangeManager
from elena.domain.services.elena import Elena
from elena.shared.dynamic_loading import get_instance


def main(home: Optional[str] = None):
    config = LocalConfigReader(home).config

    logger = get_instance(config["Logger"]["class"])
    logger.init(config)

    bot_manager = LocalBotManager(config=config, logger=logger)
    exchange_manager = CctxExchangeManager(config=config, logger=logger)

    elena = Elena(
        config=config,
        logger=logger,
        bot_manager=bot_manager,
        exchange_manager=exchange_manager,
    )
    elena.run()


if __name__ == "__main__":
    main()
