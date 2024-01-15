import typing as t
from typing import Protocol

from elena.domain.model.exchange import Exchange, ExchangeType


class StrategyManager(Protocol):
    def get_exchange(self, exchange_id: ExchangeType) -> t.Optional[Exchange]:
        ...
