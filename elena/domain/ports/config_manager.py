from typing import Dict, Protocol


class ConfigManager(Protocol):
    def init(self, url: str):
        ...

    @property
    def config(self) -> Dict:
        ...
