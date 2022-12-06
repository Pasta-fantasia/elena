from typing import Dict, List, Tuple

from elena.domain.model.bot_config import BotConfig
from elena.domain.model.exchange import Exchange
from elena.domain.model.strategy_config import StrategyConfig
from elena.domain.model.tag import Tag
from elena.domain.model.trading_pair import TradingPair


class ConfigLoader:

    def __init__(self, config: Dict):
        self._tags, self._tag_ids = self._load_tags(config)
        self._strategies = self._load_strategies(config)
        self._exchanges = self._load_exchanges(config)

    @property
    def tags(self) -> List[Tag]:
        return self._tags

    @property
    def strategies(self) -> List[StrategyConfig]:
        return self._strategies

    @property
    def exchanges(self) -> List[Exchange]:
        return self._exchanges

    @staticmethod
    def _load_tags(config) -> Tuple[List[Tag], List[str]]:
        _results = []
        for _dict in config['Tags']:
            _tag = Tag(
                id=_dict['id'],
                enabled=_dict['enabled'],
            )
            if _tag.enabled:
                _results.append(_tag)
        _ids = [tag.id for tag in _results]
        return _results, _ids

    def _load_strategies(self, config: Dict) -> List[StrategyConfig]:
        _results = []
        for _dict in config['Strategies']:
            _strategy = StrategyConfig(
                id=_dict['id'],
                name=_dict['name'],
                enabled=_dict['enabled'],
                bots=self._load_bots(_dict['bots'], _dict['id'])
            )
            if _strategy.enabled:
                _results.append(_strategy)
        return _results

    def _load_bots(self, bots: List[Dict], strategy_id: str) -> List[BotConfig]:
        _results = []
        for _dict in bots:
            _bot = BotConfig(
                id=_dict['id'],
                name=_dict['name'],
                strategy_id=strategy_id,
                enabled=_dict['enabled'],
                pair=TradingPair.build(_dict['pair']),
                exchange_id=_dict['exchange'],
                tags=_dict['tags'],
                config=_dict['config'],
            )
            if self._enabled(_bot):
                _results.append(_bot)
        return _results

    def _enabled(self, bot: BotConfig) -> bool:
        _match = set(self._tag_ids).intersection(bot.tags)
        return bot.enabled and _match

    @staticmethod
    def _load_exchanges(config) -> List[Exchange]:
        _results = []
        for _dict in config['Exchanges']:
            _exchange = Exchange(
                id=_dict['id'],
                enabled=_dict['enabled'],
                api_key=_dict['api_key'],
            )
            if _exchange.enabled:
                _results.append(_exchange)
        return _results
