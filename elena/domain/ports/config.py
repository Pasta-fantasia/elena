from typing import Protocol, Dict


class Config(Protocol):
    def get_section(self, section_name: str) -> Dict:
        pass

    def get(self, section_name: str, key: str, default_value=None):
        pass
