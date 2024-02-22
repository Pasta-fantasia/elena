from elena.domain.model.exchange import ExchangeType
from elena.domain.services.config_loader import ConfigLoader
from unittest.mock import Mock, call
from elena.domain.ports.logger import Logger


def test_load_tags():
    config = {
        "Tags": [
            {
                "id": "enabled_tag",
                "enabled": True,
            },
            {
                "id": "disabled_tag",
                "enabled": False,
            },
        ],
        "Strategies": [],
        "Exchanges": [],
    }
    logger = Mock(spec=Logger)

    sut = ConfigLoader(config, logger)

    actual = sut.tags
    assert len(actual) == 1
    assert actual[0].id == "enabled_tag"
    assert actual[0].enabled is True
    assert len(logger.mock_calls) == 1
    assert logger.mock_calls == [call.info("Skipping tag %s", "disabled_tag")]


def test_load_strategies():
    config = {
        "Tags": [
            {
                "id": "enabled_tag",
                "enabled": True,
            },
            {
                "id": "disabled_tag",
                "enabled": False,
            },
        ],
        "Strategies": [
            {
                "id": "strategy1",
                "name": "Strategy 1",
                "enabled": True,
                "strategy_class": "elena.strategies.strategy1.Strategy1",
                "bots": [
                    {
                        "id": "bot1",
                        "name": "Bot 1",
                        "enabled": True,
                        "pair": "BTC/USDT",
                        "exchange": "binance",
                        "time_frame": "1m",
                        "cron_expression": "*/5 * * * *",
                        "budget_limit": 0.0,
                        "pct_reinvest_profit": 100.0,
                        "tags": [
                            "enabled_tag",
                        ],
                        "config": {
                            "band_length": 13,
                            "band_mult": 1,
                        },
                    },
                    {
                        "id": "bot2",
                        "name": "Bot 2",
                        "enabled": False,
                        "pair": "BTC/USDT",
                        "exchange": "binance",
                        "time_frame": "1m",
                        "cron_expression": "*/5 * * * *",
                        "budget_limit": 0.0,
                        "pct_reinvest_profit": 100.0,
                        "tags": [
                            "enabled_tag",
                        ],
                        "config": {
                            "band_length": 13,
                            "band_mult": 1,
                        },
                    },
                    {
                        "id": "bot3",
                        "name": "Bot 3",
                        "enabled": True,
                        "pair": "BTC/USDT",
                        "exchange": "binance",
                        "time_frame": "1m",
                        "cron_expression": "*/5 * * * *",
                        "budget_limit": 0.0,
                        "pct_reinvest_profit": 100.0,
                        "tags": [
                            "disabled_tag",
                        ],
                        "config": {
                            "band_length": 13,
                            "band_mult": 1,
                        },
                    },
                ],
            },
            {
                "id": "strategy2",
                "name": "Strategy 2",
                "enabled": False,
                "strategy_class": "elena.strategies.strategy2.Strategy2",
                "bots": [
                    {
                        "id": "bot3",
                        "name": "Bot 3",
                        "enabled": True,
                        "pair": "BTC/USDT",
                        "exchange": "binance",
                        "time_frame": "1m",
                        "cron_expression": "*/5 * * * *",
                        "budget_limit": 0.0,
                        "pct_reinvest_profit": 100.0,
                        "tags": [
                            "enabled_tag",
                        ],
                        "config": {
                            "band_length": 13,
                            "band_mult": 1,
                        },
                    },
                ],
            },
        ],
        "Exchanges": [],
    }
    logger = Mock(spec=Logger)

    sut = ConfigLoader(config, logger)

    actual = sut.strategies
    assert len(actual) == 1
    assert actual[0].id == "strategy1"
    assert len(actual[0].bots) == 1
    assert actual[0].bots[0].id == "bot1"
    assert len(logger.mock_calls) == 4
    assert logger.mock_calls == [
        call.info("Skipping tag %s", "disabled_tag"),
        call.info("Skipping bot %s: %s", "bot2", "Bot 2"),
        call.info("Skipping bot %s: %s", "bot3", "Bot 3"),
        call.info("Skipping strategy %s: %s", "strategy2", "Strategy 2"),
    ]


def test_load_exchanges():
    config = {
        "Tags": [],
        "Strategies": [],
        "Exchanges": [
            {
                "id": "binance",
                "enabled": True,
                "sandbox_mode": False,
                "api_key": "EXCHANGE_API_KEY",
                "password": "EXCHANGE_PASSWORD",
                "secret": "EXCHANGE_SECRET",
            },
            {
                "id": "coinbase",
                "enabled": False,
                "sandbox_mode": False,
                "api_key": "EXCHANGE_API_KEY",
                "password": "EXCHANGE_PASSWORD",
                "secret": "EXCHANGE_SECRET",
            },
        ],
    }
    logger = Mock(spec=Logger)

    sut = ConfigLoader(config, logger)

    actual = sut.exchanges
    assert len(actual) == 1
    assert actual[0].id == "binance"
    assert len(logger.mock_calls) == 1
    assert logger.mock_calls == [call.info("Skipping exchange %s", ExchangeType.coinbase)]
