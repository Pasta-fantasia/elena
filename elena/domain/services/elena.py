import logging

from elena.domain.ports.config import Config


class Elena:

    def __init__(self, config: Config):
        self._config = config
        logging.info("Elena initialized")

    def run(self):
        _profile = self._config.get("Common", 'profile')
        logging.info(f"Starting Elena on {_profile} profile.")
