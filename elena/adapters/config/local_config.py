import os
import pathlib
from os import path
from typing import Dict, List

import yaml

from elena.domain.model.bot_config import BotConfig
from elena.domain.model.strategy_config import StrategyConfig
from elena.domain.model.trading_pair import TradingPair
from elena.domain.ports.config import Config


class LocalConfig(Config):

    def __init__(self, home: str):
        self._home = self._get_home(home)
        default_config = self._load_default_config()
        user_config = self._load_user_config()
        self._config = {**default_config, **user_config}

    @property
    def home(self) -> str:
        return self._home

    @staticmethod
    def _get_home(home: str) -> str:
        if home:
            print(f'Loading config from `home` parameter `{home}`')
            return home
        home = os.environ.get('ELENA_HOME')
        if home:
            print(f'Loading config from ELENA_HOME `{home}`')
        else:
            home = os.getcwd()
            print(f'Loading config from current directory `{home}`')
        return home

    def _load_default_config(self) -> Dict:
        _dir = path.join(pathlib.Path(__file__).parent.parent.parent.absolute(), 'config')
        _file = path.join(_dir, 'default_config.yaml')
        return self._load_yaml(_file)

    def _load_user_config(self) -> Dict:
        _file = path.join(self._home, 'config.yaml')
        return self._load_yaml(_file)

    @staticmethod
    def _load_yaml(file: str) -> Dict:
        with open(file, 'r') as f:
            _yaml = yaml.safe_load(f)
        return _yaml

    def get(self, section_name: str, key: str, default_value=None):
        try:
            _value = self._config[section_name][key]
        except KeyError:
            return default_value
        if _value:
            return _value
        else:
            return default_value

    def get_strategies(self) -> List[StrategyConfig]:
        _results = []
        for _dict in self._config['Strategies']:
            _strategy = StrategyConfig(
                strategy_id=_dict['strategy_id'],
                name=_dict['name'],
                enabled=_dict['enabled'],
                bots=self._get_bots(_dict['bots'], _dict['strategy_id'])
            )
            _results.append(_strategy)
        return _results

    @staticmethod
    def _get_bots(bots: List[Dict], strategy_id: str) -> List[BotConfig]:
        _results = []
        for _dict in bots:
            _bot = BotConfig(
                bot_id=_dict['bot_id'],
                name=_dict['name'],
                strategy_id=strategy_id,
                enabled=_dict['enabled'],
                pair=TradingPair.build(_dict['pair']),
                config=_dict['config'],
            )
            _results.append(_bot)
        return _results
