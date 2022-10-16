import logging
import pathlib
from os import path
from typing import Dict, List

import yaml

from elena.domain.model.bot_config import BotConfig
from elena.domain.model.strategy_config import StrategyConfig
from elena.domain.ports.config import Config


class LocalConfig(Config):

    def __init__(self, profile: str):
        default_cfg = self._load_default_cfg(profile)
        user_cfg = self._load_user_cfg(profile)
        self._config = {**default_cfg, **user_cfg}
        logging.info(f'Loaded {profile} configuration')

    def _load_default_cfg(self, profile: str) -> Dict:
        return self._load_yaml(f'{profile}-default.yaml')

    def _load_user_cfg(self, profile: str) -> Dict:
        return self._load_yaml(f'{profile}-user.yaml')

    @staticmethod
    def _load_yaml(filename: str) -> Dict:
        _dir = path.join(pathlib.Path(__file__).parent.parent.parent.parent.absolute(), 'cfg')
        _file = path.join(_dir, filename)
        with open(_file, 'r') as f:
            _yaml = yaml.safe_load(f)
        logging.info(f'Loaded configuration from {_file}')
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
            logging.debug('OBJ: %s', _strategy)
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
                config=_dict['config'],
            )
            _results.append(_bot)
        return _results