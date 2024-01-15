from datetime import datetime

import pandas as pd
import pytest

from elena.adapters.exchange_manager.cctx_exchange_manager import CctxExchangeManager
from elena.domain.model.time_frame import TimeFrame


@pytest.mark.parametrize(
    "last_candle_time,now,time_frame,expected",
    [
        (
            datetime(2023, 12, 31, 17, 56),
            datetime(2023, 12, 31, 17, 56),
            TimeFrame.min_1,
            True,
        ),
        (
            datetime(2023, 12, 31, 17, 56, 0),
            datetime(2023, 12, 31, 17, 56, 59),
            TimeFrame.min_1,
            True,
        ),
        (
            datetime(2023, 12, 31, 17, 56),
            datetime(2023, 12, 31, 17, 57),
            TimeFrame.min_1,
            False,
        ),
        (
            datetime(2023, 12, 31, 17, 56),
            datetime(2023, 12, 31, 17, 56),
            TimeFrame.hour_1,
            True,
        ),
        (
            datetime(2023, 12, 31, 17, 0),
            datetime(2023, 12, 31, 17, 59),
            TimeFrame.hour_1,
            True,
        ),
        (
            datetime(2023, 12, 31, 17, 56),
            datetime(2023, 12, 31, 18, 56),
            TimeFrame.hour_1,
            False,
        ),
        (
            datetime(2023, 12, 31, 17, 56),
            datetime(2023, 12, 31, 17, 56),
            TimeFrame.day_1,
            True,
        ),
        (
            datetime(2023, 12, 31, 0, 0),
            datetime(2023, 12, 31, 23, 59),
            TimeFrame.day_1,
            True,
        ),
        (
            datetime(2023, 12, 30, 17, 56),
            datetime(2023, 12, 31, 17, 56),
            TimeFrame.day_1,
            False,
        ),
        (
            datetime(2023, 12, 31, 17, 56),
            datetime(2023, 12, 31, 17, 56),
            TimeFrame.month_1,
            True,
        ),
        (
            datetime(2023, 12, 1, 17, 56),
            datetime(2023, 12, 31, 17, 56),
            TimeFrame.month_1,
            True,
        ),
        (
            datetime(2023, 11, 30, 17, 56),
            datetime(2023, 12, 31, 17, 56),
            TimeFrame.day_1,
            False,
        ),
        (
            datetime(2023, 11, 30, 17, 56),
            datetime(2023, 12, 1, 17, 56),
            TimeFrame.day_1,
            False,
        ),
        (
            datetime(2023, 12, 31, 17, 56),
            datetime(2024, 12, 31, 17, 56),
            TimeFrame.month_1,
            False,
        ),
        (
            datetime(2023, 12, 31, 17, 56),
            datetime(2023, 12, 31, 17, 56),
            TimeFrame.year_1,
            True,
        ),
        (
            datetime(2023, 12, 31, 17, 56),
            datetime(2024, 1, 1, 0, 0),
            TimeFrame.year_1,
            False,
        ),
        (
            datetime(2023, 12, 31, 17, 56),
            datetime(2024, 12, 31, 17, 56),
            TimeFrame.year_1,
            False,
        ),
    ],
)
def test_are_stored_candles_up_to_date(last_candle_time, now, time_frame, expected):
    candles_data = {
        "Open time": {
            0: 1702479180000,
            1: 1702479240000,
            2: 1702479300000,
            3: 1702479360000,
            4: 1702479420000,
            5: int(datetime.timestamp(last_candle_time) * 1000),
        },
        "Open": {
            0: 41372.86,
            1: 41350.92,
            2: 41353.37,
            3: 41357.66,
            4: 41345.54,
            5: 41374.01,
        },
        "High": {
            0: 41381.04,
            1: 41353.37,
            2: 41357.35,
            3: 41357.66,
            4: 41378.94,
            5: 41378.8,
        },
        "Low": {
            0: 41354.07,
            1: 41339.94,
            2: 41345.76,
            3: 41345.54,
            4: 40757.6,
            5: 41371.49,
        },
        "Close": {
            0: 41354.07,
            1: 41353.37,
            2: 41357.35,
            3: 41347.93,
            4: 41378.86,
            5: 41371.49,
        },
        "Volume": {
            0: 0.3119400144,
            1: 0.3297800124,
            2: 0.2395299971,
            3: 0.1104699969,
            4: 0.7769600153,
            5: 0.1653700024,
        },
    }
    stored_candles = pd.DataFrame(candles_data)
    assert CctxExchangeManager._are_stored_candles_up_to_date(stored_candles, time_frame, now) == expected
