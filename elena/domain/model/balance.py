from typing import Dict, Set

from pydantic import BaseModel

from elena.domain.model.currency import Currency


class ByAvailability(BaseModel):
    currency: Currency
    amount: float


class ByCurrency(BaseModel):
    free: float
    used: float
    total: float


class Balance(BaseModel):
    timestamp: int  # Unix timestamp in milliseconds
    free: Set[ByAvailability]  # money, available for trading, by currency
    used: Set[ByAvailability]  # money on hold, locked, frozen, or pending, by currency
    total: Set[ByAvailability]  # total (free + used), by currency
    currencies: Dict[Currency, ByCurrency]  # balance indexed by currency
    info: Dict  # the original untouched non-parsed reply with details
