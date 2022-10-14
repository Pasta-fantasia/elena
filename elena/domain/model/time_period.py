from pydantic.validators import IntEnum


class TimePeriod(IntEnum):
    min_1 = 1
    min_5 = 5
    min_15 = 15
    min_30 = 30
    hour_1 = 60
    hour_8 = 8*60
    hour_12 = 12*60
    hour_24 = 24*60
    week_1 = 7*24*60
