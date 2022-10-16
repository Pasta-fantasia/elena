import logging
from typing import Tuple

from elena.domain.model.Error import Error
from elena.domain.model.order import Order
from elena.domain.model.summary import Summary
from elena.domain.ports.emit_flesti import EmitFlesti
from elena.domain.ports.order_writer import OrderWriter


class KuCoinOrderWriter(OrderWriter):

    def __init__(self, emit_flesti: EmitFlesti):
        self._emit_flesti = emit_flesti

    def write(self, order: Order) -> Tuple[Summary, Error]:
        logging.info('Writing order %s to KuCoin', order)
        # TODO Implement me!!
        _summary = Summary(
            bot_id=order.bot_id,
            strategy_id=order.strategy_id,
            summary={}
        )
        return _summary, Error.none()
