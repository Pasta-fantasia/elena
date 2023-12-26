from typing import Dict, Protocol, runtime_checkable


@runtime_checkable
class ConfigManager(Protocol):
    def init(self, url: str):
        ...

    def get_config(self) -> Dict:
        ...
