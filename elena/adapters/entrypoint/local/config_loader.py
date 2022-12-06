import os
import pathlib
from os import path
from typing import Dict

import yaml


class LocalConfigLoader:

    def __init__(self):
        home = self._get_home()
        default_config = self._load_default_config()
        user_config = self._load_user_config(home)
        config = {**default_config, **user_config}
        self._config = self._update_config_with_home(config, home)

    @property
    def config(self) -> Dict:
        return self._config

    @staticmethod
    def _get_home() -> str:
        home = os.environ.get('ELENA_HOME')
        if home:
            print(f'Loading config from ELENA_HOME `{home}`')
        else:
            home = os.getcwd()
            print(f'Loading config from current directory `{home}`')
        return home

    def _load_default_config(self) -> Dict:
        _dir = path.join(pathlib.Path(__file__).parent.parent.parent.parent.absolute(), 'config')
        _file = path.join(_dir, 'default_config.yaml')
        return self._load_yaml(_file)

    def _load_user_config(self, home: str) -> Dict:
        _file = path.join(home, 'external_config.yaml')
        return self._load_yaml(_file)

    @staticmethod
    def _load_yaml(file: str) -> Dict:
        with open(file, 'r') as f:
            _yaml = yaml.safe_load(f)
        return _yaml

    @staticmethod
    def _update_config_with_home(config: Dict, home: str) -> Dict:
        config['LocalLogger']['path'] = path.join(home, config['LocalLogger']['path'])
        config['LocalBotManager']['path'] = path.join(home, config['LocalBotManager']['path'])
        return config
