import logging
from typing import Tuple

from elena.domain.model.Error import Error
from elena.domain.model.order import Order
from elena.domain.model.summary import Summary
from elena.domain.ports.order_writer import OrderWriter


class KuCoinOrderWriter(OrderWriter):

    def write(self, order: Order) -> Tuple[Summary, Error]:
        logging.info('Writing order %s to KuCoin', order)
        # TODO Implement me!!
        return Error.none()
