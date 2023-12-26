import pathlib
from os import path
from typing import Dict

import yaml  # type: ignore

from elena.domain.ports.config_manager import ConfigManager


class LocalConfigManager(ConfigManager):
    _config: Dict

    def init(self, url: str):
        home_config = {"home": url}
        base_config = self._load_base_config(url)
        strategies = self._load_config(url, "strategies.yaml")
        secrets = self._load_config(url, "secrets.yaml")
        self._config = {**home_config, **base_config, **strategies, **secrets}
        self._filter_entries()

    @property
    def config(self) -> Dict:
        return self._config

    def _load_config(self, home: str, filename: str) -> Dict:
        file = path.join(home, filename)
        print(f"Loading config from `{file}`")
        return self._load_yaml(file)

    @staticmethod
    def _load_yaml(file: str) -> Dict:
        with open(file, "r") as f:
            yaml_content = yaml.safe_load(f)
        return yaml_content

    def _filter_entries(self):
        allowed_entries = [
            "home",
            "Logger",
            "MetricsManager",
            "NotificationsManager",
            "BotManager",
            "ExchangeManager",
            "Exchanges",
            "Strategies",
            "Tags",
        ]
        for key in list(self._config.keys()):
            if key not in allowed_entries:
                del self._config[key]

    def _load_default_config(self) -> Dict:
        _dir = path.join(pathlib.Path(__file__).parent.parent.parent.absolute(), "config")
        file = path.join(_dir, "default_config.yaml")
        return self._load_yaml(file)

    def _load_base_config(self, home: str) -> Dict:
        default_config = self._load_default_config()
        config = self._load_config(home, "config.yaml")
        base_config = {**default_config, **config}
        return base_config
