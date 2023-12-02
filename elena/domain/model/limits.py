from pydantic import BaseModel


class Field(BaseModel):
    min: float
    max: float


class Limits(BaseModel):
    """Value limits when placing orders on this market"""

    amount: Field
    price: Field
    cost: Field
    leverage: Field
