from typing import Dict

from elena.domain.model.order import Order
from elena.domain.model.summary import Summary
from elena.domain.ports.logger import Logger
from elena.domain.ports.order_writer import OrderWriter


class CctxOrderWriter(OrderWriter):

    def __init__(self, config: Dict, logger: Logger):
        self._config = config
        self._logger = logger

    def write(self, order: Order) -> Summary:
        self._logger.info('Writing order with CCTX: bot %s strategy %s', order.bot_id, order.strategy_id)
        # TODO Implement me!!
        _summary = Summary(
            bot_id=order.bot_id,
            strategy_id=order.strategy_id,
            summary={}
        )
        return _summary
