from datetime import datetime
from unittest.mock import patch

from elena.domain.services.strategy_manager import StrategyManagerImpl


def test__check_if_bot_has_to_run():
    """
    With a cron expression configured to run every 5th minute
    the last execution time set to 10:05:00
    and patching the current time to 10:10:00
    the bot should run.
    """
    last_execution = datetime(2020, 1, 1, 10, 5, 0)
    with (patch("elena.domain.services.strategy_manager.datetime") as mock_datetime):
        mock_datetime.now.return_value = datetime(2020, 1, 1, 10, 10, 0)
        actual = StrategyManagerImpl._check_if_bot_has_to_run(
            last_execution=last_execution, cron_expression="*/5 * * * *"
        )
    assert actual is True


def test__check_if_bot_has_to_run_one_intermediate_run_is_missing():
    """
    With a cron expression configured to run every 5th minute
    the last execution time set to 10:05:00
    and patching the current time to 10:20:00
    the bot should run.
    """
    last_execution = datetime(2020, 1, 1, 10, 5, 0)
    with (patch("elena.domain.services.strategy_manager.datetime") as mock_datetime):
        mock_datetime.now.return_value = datetime(2020, 1, 1, 20, 10, 0)
        actual = StrategyManagerImpl._check_if_bot_has_to_run(
            last_execution=last_execution, cron_expression="*/5 * * * *"
        )
    assert actual is True


def test__check_if_bot_has_to_do_not_run():
    """
    With a cron expression configured to run every 5th minute
    the last execution time set to 10:05:00
    and patching the current time to 10:09:00
    the bot should run.
    """
    last_execution = datetime(2020, 1, 1, 10, 5, 0)
    with patch("elena.domain.services.strategy_manager.datetime") as mock_datetime:
        mock_datetime.now.return_value = datetime(2020, 1, 1, 10, 9, 0)
        actual = StrategyManagerImpl._check_if_bot_has_to_run(
            last_execution=last_execution, cron_expression="*/5 * * * *"
        )

    assert actual is False


def test__check_if_bot_has_to_do_not_run_by_one_second():
    """
    With a cron expression configured to run every 5th minute
    the last execution time set to 10:05:00
    and patching the current time to 10:09:59
    the bot should run.
    """
    last_execution = datetime(2020, 1, 1, 10, 5, 0)
    with patch("elena.domain.services.strategy_manager.datetime") as mock_datetime:
        mock_datetime.now.return_value = datetime(2020, 1, 1, 10, 9, 59)
        actual = StrategyManagerImpl._check_if_bot_has_to_run(
            last_execution=last_execution, cron_expression="*/5 * * * *"
        )

    assert actual is False
