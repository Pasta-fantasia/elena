from typing import Tuple

from elena.domain.model.Error import Error
from elena.domain.model.order import Order
from elena.domain.model.summary import Summary
from elena.domain.ports.config import Config
from elena.domain.ports.logger import Logger
from elena.domain.ports.order_writer import OrderWriter


class KuCoinOrderWriter(OrderWriter):

    def __init__(self, config: Config, logger: Logger):
        self._config = config
        self._logger = logger

    def write(self, order: Order) -> Tuple[Summary, Error]:
        self._logger.info('Writing order %s to KuCoin', order)
        # TODO Implement me!!
        _summary = Summary(
            bot_id=order.bot_id,
            strategy_id=order.strategy_id,
            summary={}
        )
        return _summary, Error.none()
