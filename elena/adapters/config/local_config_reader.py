import os
import pathlib
from os import path
from typing import Dict, List, Optional

import yaml  # type: ignore


class LocalConfigReader:
    def __init__(self, home: Optional[str] = None):
        if not home:
            home = self._get_home()
        base_config = self._load_base_config(home)
        strategies = self._load_strategies(home)
        secrets = self._load_secrets(home)
        config = {**base_config, **strategies, **secrets}
        self._config = self._update_config_with_home(config, home)

    @property
    def config(self) -> Dict:
        return self._config

    @staticmethod
    def _get_home() -> str:
        home = os.environ.get("ELENA_HOME")
        if home:
            print(f"Loading config from ELENA_HOME `{home}`")
        else:
            home = os.getcwd()
            print(f"Loading config from current directory `{home}`")
        return home

    def _load_config(self, home: str, filename: str) -> Dict:
        file = path.join(home, filename)
        return self._load_yaml(file)

    @staticmethod
    def _load_yaml(file: str) -> Dict:
        with open(file, "r") as f:
            yaml_content = yaml.safe_load(f)
        return yaml_content

    @staticmethod
    def _filter_entries(config: Dict, allowed_entries: List[str]) -> Dict:
        for key in list(config.keys()):
            if key not in allowed_entries:
                del config[key]
        return config

    def _load_default_config(self) -> Dict:
        _dir = path.join(
            pathlib.Path(__file__).parent.parent.parent.absolute(), "config"
        )
        file = path.join(_dir, "default_config.yaml")
        return self._load_yaml(file)

    def _load_base_config(self, home: str) -> Dict:
        default_config = self._load_default_config()
        config = self._load_config(home, "config.yaml")
        config = self._filter_entries(
            config, ["LocalLogger", "LocalBotManager", "CctxExchangeManager"]
        )
        base_config = {**default_config, **config}
        return base_config

    def _load_strategies(self, home: str) -> Dict:
        strategies = self._load_config(home, "strategies.yaml")
        strategies = self._filter_entries(strategies, ["Strategies", "Tags"])
        return strategies

    def _load_secrets(self, home: str) -> Dict:
        strategies = self._load_config(home, "secrets.yaml")
        strategies = self._filter_entries(strategies, ["Exchanges"])
        return strategies

    @staticmethod
    def _update_config_with_home(config: Dict, home: str) -> Dict:
        config["LocalLogger"]["path"] = path.join(home, config["LocalLogger"]["path"])
        config["LocalBotManager"]["path"] = path.join(
            home, config["LocalBotManager"]["path"]
        )
        return config
