import json
import pathlib
from os import path
from unittest.mock import patch, Mock, call, ANY

import pytest

from elena.domain.model.bot_status import BotStatus, BotBudget
from elena.domain.model.order import Order, OrderSide, OrderType
from elena.domain.model.trading_pair import TradingPair
from elena.domain.ports.metrics_manager import ORDER_CANCELLED
from elena.domain.services.elena import get_storage_manager


@pytest.fixture
def logger():
    return Mock()


@pytest.fixture
def storage_manager(logger):
    sut = get_storage_manager(
        config={
            "home": path.join(pathlib.Path(__file__).parent.parent.parent.parent, "test_home"),
            "StorageManager": {
                "class": "elena.adapters.storage_manager.local_storage_manager.LocalStorageManager",
                "path": "storage",
            },
        },
        logger=logger,
    )

    return sut


def test_save_and_load_bot_status(logger, storage_manager):
    bot_status = BotStatus(
        bot_id="test_bot_id",
        timestamp=1703944135288,
        active_orders=[
            Order(
                id="3448098",
                exchange_id="binance",
                bot_id="Exchange_Test_Ops_BTC_USDT",
                strategy_id="ExchangeBasicOperationsTest-1",
                pair=TradingPair(base="BTC", quote="USDT"),
                timestamp=1702485175960,
                type=OrderType.stop_loss_limit,
                side=OrderSide.sell,
                price=31972.77,
                amount=0.00945,
                cost=0.0,
                average=None,
                filled=0.0,
                remaining=0.00945,
                status="canceled",
                fee=None,
                trigger_price=33655.54,
                stop_price=33655.54,
                take_profit_price=None,
                stop_loss_price=None,
            )
        ],
        archived_orders=[
            Order(
                id="3448099",
                exchange_id="binance",
                bot_id="Exchange_Test_Ops_BTC_USDT",
                strategy_id="ExchangeBasicOperationsTest-1",
                pair=TradingPair(base="BTC", quote="USDT"),
                timestamp=1702485175960,
                type=OrderType.stop_loss_limit,
                side=OrderSide.sell,
                price=31972.77,
                amount=0.00945,
                cost=0.0,
                average=None,
                filled=0.0,
                remaining=0.00945,
                status="canceled",
                fee=None,
                trigger_price=33655.54,
                stop_price=33655.54,
                take_profit_price=None,
                stop_loss_price=None,
            )
        ],
        active_trades=[],
        closed_trades=[],
        budget=BotBudget(),
    )

    storage_manager.save_bot_status(bot_status)

    actual = storage_manager.load_bot_status(bot_status.bot_id)
    assert actual == bot_status

    assert logger.mock_calls == [
        call.info("LocalStorageManager working at %s", ANY),
        call.debug("Saving %s %s to storage: %s", "BotStatus", "test_bot_id", ANY),
        call.debug("Loading %s %s from storage: %s", "BotStatus", "test_bot_id", ANY),
    ]


def test_append_metric(logger, storage_manager):
    filepath = path.join(pathlib.Path(__file__).parent.parent.parent.parent, "test_home", "storage", "Metric", "test_append_metric_bot", "240119.jsonl")
    try:
        pathlib.Path(filepath).unlink()
    except FileNotFoundError:
        pass

    with patch("elena.adapters.storage_manager.file_storage_manager.time") as mocked_datetime:
        mocked_datetime.time.return_value = 1705685253
        mocked_datetime.strftime.return_value = "240119"
        storage_manager.append_metric("test_append_metric_bot", ORDER_CANCELLED, "counter", 1, ["tag1:abc", "tag2:def"])
        storage_manager.append_metric("test_append_metric_bot", ORDER_CANCELLED, "gauge", 77, ["tag1:abc", "tag2:def"])

    with open(filepath) as reader:
        lines = reader.read().splitlines()

    assert len(lines) == 2
    assert json.loads(lines[0]) == {
        "timestamp": 1705685253000,
        "bot_id": "test_append_metric_bot",
        "metric_name": "OrderCancelled",
        "metric_type": "counter",
        "value": 1,
        "tags": "tag1:abc#tag2:def",
    }
    assert json.loads(lines[1]) == {
        "timestamp": 1705685253000,
        "bot_id": "test_append_metric_bot",
        "metric_name": "OrderCancelled",
        "metric_type": "gauge",
        "value": 77,
        "tags": "tag1:abc#tag2:def",
    }

    assert logger.mock_calls == [
        call.info("LocalStorageManager working at %s", ANY),
    ]
