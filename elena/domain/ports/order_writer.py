from typing import Protocol

from elena.domain.model.order import Order
from elena.domain.model.summary import Summary


class OrderWriter(Protocol):

    def write(self, order: Order) -> Summary:
        """
        Places an order to an Exchange
        :param order: the order definition to write
        :return: the summary with the result of the order placement, and error if any
        """
        pass
