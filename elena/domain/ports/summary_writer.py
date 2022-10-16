from typing import Protocol

from elena.domain.model.Error import Error
from elena.domain.model.summary import Summary


class SummaryWriter(Protocol):

    def write(self, summary: Summary) -> Error:
        """
        Persists a summary of an order
        :param summary: the summary
        :return: error if any
        """
        pass
