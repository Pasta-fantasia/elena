import logging

from elena.domain.model.Error import Error
from elena.domain.model.summary import Summary
from elena.domain.ports.summary_writer import SummaryWriter


class LocalSummaryWriter(SummaryWriter):

    def write(self, summary: Summary) -> Error:
        logging.info('Writing %s bot summary to disk', summary.bot_id)
        # TODO Implement me!!
        return Error.none()