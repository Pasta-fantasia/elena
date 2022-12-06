from pydantic.config import Enum


class TimeFrame(str, Enum):
    min_1 = '1m'
    hour_1 = '1h'
    day_1 = '1d'
    month_1 = '1M'
    year_1 = '1y'
