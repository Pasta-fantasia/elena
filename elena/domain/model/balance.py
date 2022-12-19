from typing import Dict, List

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
    timestamp: int  # Unix Timestamp in milliseconds since Epoch 1 Jan 1970
    free: List[ByAvailability]  # money, available for trading, by currency
    used: List[ByAvailability]  # money on hold, locked, frozen, or pending, by currency
    total: List[ByAvailability]  # total (free + used), by currency
    currencies: Dict[Currency, ByCurrency]  # balance indexed by currency
    info: Dict  # the original untouched non-parsed reply with details
