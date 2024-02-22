import json
import pathlib
from os import path
from unittest.mock import patch

from mockito import mock

from elena.domain.ports.metrics_manager import ORDER_CANCELLED
from elena.domain.services.elena import get_metrics_manager, get_storage_manager

config = {
    "home": path.join(pathlib.Path(__file__).parent.parent.parent.parent, "test_home"),
    "StorageManager": {
        "class": "elena.adapters.storage_manager.local_storage_manager.LocalStorageManager",
        "path": "storage",
    },
    "MetricsManager": {
        "class": "elena.adapters.metrics_manager.local_metrics_manager.LocalMetricsManager",
    },
}


def test_metrics():
    storage_manager = get_storage_manager(
        config=config,
        logger=mock(),
    )
    sut = get_metrics_manager(
        config=config,
        logger=mock(),
        storage_manager=storage_manager,
    )

    filepath = path.join(pathlib.Path(__file__).parent.parent.parent.parent, "test_home", "storage", "Metric", "test_bot", "240119.jsonl")
    try:
        pathlib.Path(filepath).unlink()
    except FileNotFoundError:
        pass

    with patch("elena.adapters.storage_manager.file_storage_manager.time") as mocked_datetime:
        mocked_datetime.time.return_value = 1705685253
        mocked_datetime.strftime.return_value = "240119"
        sut.counter(ORDER_CANCELLED, "test_bot", 7, ["tag1:abc", "tag2:jaja"])
        sut.gauge(ORDER_CANCELLED, "test_bot", 9.9, ["tag1:cde", "tag2:jiji"])

    with open(filepath) as reader:
        lines = reader.read().splitlines()

    assert len(lines) == 2
    assert json.loads(lines[0]) == {
        "timestamp": 1705685253000,
        "bot_id": "test_bot",
        "metric_name": "OrderCancelled",
        "metric_type": "counter",
        "value": 7,
        "tags": "tag1:abc#tag2:jaja",
    }
    assert json.loads(lines[1]) == {
        "timestamp": 1705685253000,
        "bot_id": "test_bot",
        "metric_name": "OrderCancelled",
        "metric_type": "gauge",
        "value": 9.9,
        "tags": "tag1:cde#tag2:jiji",
    }
