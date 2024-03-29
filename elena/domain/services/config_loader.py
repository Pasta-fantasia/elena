from typing import Dict, List, Tuple

from elena.domain.model.bot_config import BotConfig
from elena.domain.model.exchange import Exchange, ExchangeType
from elena.domain.model.strategy_config import StrategyConfig
from elena.domain.model.tag import Tag
from elena.domain.model.time_frame import TimeFrame
from elena.domain.model.trading_pair import TradingPair
from elena.domain.ports.logger import Logger


class ConfigLoader:
    def __init__(self, config: Dict, logger: Logger):
        self._logger = logger
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

    def _load_tags(self, config) -> Tuple[List[Tag], List[str]]:
        results = []
        for tags in config["Tags"]:
            tag = Tag(
                id=tags["id"],
                enabled=tags["enabled"],
            )
            if tag.enabled:
                results.append(tag)
            else:
                self._logger.info("Skipping tag %s", tag.id)
        ids = [tag.id for tag in results]
        return results, ids

    def _load_strategies(self, config: Dict) -> List[StrategyConfig]:
        results = []
        for strategies in config["Strategies"]:
            strategy = StrategyConfig(
                id=strategies["id"],
                name=strategies["name"],
                enabled=strategies["enabled"],
                strategy_class=strategies["strategy_class"],
                bots=self._load_bots(strategies["bots"], strategies["id"]),
            )
            if strategy.enabled:
                results.append(strategy)
            else:
                self._logger.info("Skipping strategy %s: %s", strategy.id, strategy.name)
        return results

    def _load_bots(self, bots: List[Dict], strategy_id: str) -> List[BotConfig]:
        results = []
        for bot in bots:
            try:
                config = BotConfig(
                    id=bot["id"],
                    name=bot["name"],
                    strategy_id=strategy_id,
                    enabled=bot["enabled"],
                    pair=TradingPair.build(bot["pair"]),
                    exchange_id=ExchangeType(bot["exchange"]),
                    time_frame=TimeFrame(bot["time_frame"]),
                    cron_expression=bot["cron_expression"],
                    budget_limit=bot["budget_limit"],
                    pct_reinvest_profit=bot["pct_reinvest_profit"],
                    tags=bot["tags"],
                    config=bot["config"],
                )
            except KeyError as err:
                raise ValueError(f"Missing bot configuration: {err}")
            if self._enabled(config):
                results.append(config)
            else:
                self._logger.info("Skipping bot %s: %s", config.id, config.name)

        return results

    def _enabled(self, bot: BotConfig) -> bool:
        match = set(self._tag_ids).intersection(bot.tags)
        return bot.enabled and match  # type: ignore

    def _load_exchanges(self, config) -> List[Exchange]:
        results = []
        for exchanges in config["Exchanges"]:
            exchange = Exchange(
                id=exchanges["id"],
                enabled=exchanges["enabled"],
                sandbox_mode=exchanges["sandbox_mode"],
                api_key=exchanges["api_key"],
                password=exchanges["password"],
                secret=exchanges["secret"],
            )
            if exchange.enabled:
                results.append(exchange)
            else:
                self._logger.info("Skipping exchange %s", exchange.id)
        return results
