from typing import Protocol, Tuple

from elena.domain.model.Error import Error
from elena.domain.model.order import Order
from elena.domain.model.summary import Summary


class OrderWriter(Protocol):

    def write(self, order: Order) -> Tuple[Summary, Error]:
        """
        Places an order to an Exchange
        :param order: the order definition to write
        :return: the summary with the result of the order placement, and error if any
        """
        pass
