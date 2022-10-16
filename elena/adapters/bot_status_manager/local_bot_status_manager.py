import logging

from elena.domain.model.Error import Error
from elena.domain.model.bot_status import BotStatus
from elena.domain.ports.bot_status_manager import BotStatusManager
from elena.domain.ports.emit_flesti import EmitFlesti


class LocalBotStatusManager(BotStatusManager):

    def __init__(self, emit_flesti: EmitFlesti):
        self._emit_flesti = emit_flesti

    def load(self, bot_id: str) -> BotStatus:
        logging.info('Loaded %s bot status from disk', bot_id)
        # TODO Implement me!!
        return BotStatus(
            bot_id=bot_id,
            timestamp=self._emit_flesti.now(),
            status={},
        )
        pass

    def write(self, status: BotStatus) -> Error:
        logging.info('Writing %s bot status to disk', status)
        # TODO Implement me!!
        return Error.none()
