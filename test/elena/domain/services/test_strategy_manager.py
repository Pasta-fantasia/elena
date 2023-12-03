from datetime import datetime
from unittest.mock import patch

import pytest

from elena.domain.services.strategy_manager import StrategyManagerImpl


@pytest.mark.parametrize(
    "name,last_execution, now, expected",
    [
        (
            "Bot has to run, o'clock",
            datetime(2020, 1, 1, 10, 5, 0),
            datetime(2020, 1, 1, 10, 10, 0),
            True,
        ),
        (
            "Bot has to run, 1 second after",
            datetime(2020, 1, 1, 10, 5, 0),
            datetime(2020, 1, 1, 10, 10, 1),
            True,
        ),
        (
            "Bot has to run, one intermediate run is missing",
            datetime(2020, 1, 1, 10, 5, 0),
            datetime(2020, 1, 1, 20, 11, 0),
            True,
        ),
        (
            "Bot has to do not run",
            datetime(2020, 1, 1, 10, 0, 0),
            datetime(2020, 1, 1, 10, 1, 0),
            False,
        ),
        (
            "Bot has to do not run by one second",
            datetime(2020, 1, 1, 10, 5, 0),
            datetime(2020, 1, 1, 10, 9, 59),
            False,
        ),
    ],
)
def test_check_if_bot_has_to_run(name, last_execution, now, expected):
    with (patch("elena.domain.services.strategy_manager.datetime") as mock_datetime):
        mock_datetime.now.return_value = now
        actual = StrategyManagerImpl._check_if_bot_has_to_run(
            last_execution=last_execution, cron_expression="*/5 * * * *"
        )
    assert actual is expected, f"Error running test '{name}'"
