from typing import Dict, List, Tuple

from elena.domain.model.bot_config import BotConfig
from elena.domain.model.exchange import Exchange, ExchangeType
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
        results = []
        for tags in config['Tags']:
            tag = Tag(
                id=tags['id'],
                enabled=tags['enabled'],
            )
            if tag.enabled:
                results.append(tag)
        ids = [tag.id for tag in results]
        return results, ids

    def _load_strategies(self, config: Dict) -> List[StrategyConfig]:
        results = []
        for strategies in config['Strategies']:
            strategy = StrategyConfig(
                id=strategies['id'],
                name=strategies['name'],
                enabled=strategies['enabled'],
                strategy_class=strategies['strategy_class'],
                bots=self._load_bots(strategies['bots'], strategies['id'])
            )
            if strategy.enabled:
                results.append(strategy)
        return results

    def _load_bots(self, bots: List[Dict], strategy_id: str) -> List[BotConfig]:
        results = []
        for bot in bots:
            config = BotConfig(
                id=bot['id'],
                name=bot['name'],
                strategy_id=strategy_id,
                enabled=bot['enabled'],
                pair=TradingPair.build(bot['pair']),
                exchange_id=ExchangeType(bot['exchange']),
                tags=bot['tags'],
                config=bot['config'],
            )
            if self._enabled(config):
                results.append(config)
        return results

    def _enabled(self, bot: BotConfig) -> bool:
        match = set(self._tag_ids).intersection(bot.tags)
        return bot.enabled and match

    @staticmethod
    def _load_exchanges(config) -> List[Exchange]:
        results = []
        for exchanges in config['Exchanges']:
            exchange = Exchange(
                id=exchanges['id'],
                enabled=exchanges['enabled'],
                sandbox_mode=exchanges['sandbox_mode'],
                api_key=exchanges['api_key'],
                password=exchanges['password'],
                secret=exchanges['secret'],
            )
            if exchange.enabled:
                results.append(exchange)
        return results
