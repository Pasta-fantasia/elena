import pathlib
from os import path

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


def test_counter():
    storage_manager = get_storage_manager(
        config=config,
        logger=mock(),
    )
    sut = get_metrics_manager(
        config=config,
        logger=mock(),
        storage_manager=storage_manager,
    )

    strategy_id = "test_strategy"
    df_id = f"Counter-{ORDER_CANCELLED}-{strategy_id}"

    try:
        storage_manager.delete_data_frame(df_id)
    except Exception:
        pass

    sut.counter(ORDER_CANCELLED, strategy_id, 7, ["tag7"])

    actual = storage_manager.load_data_frame(df_id).to_dict()
    assert len(actual) == 3
    assert "time" in actual
    assert actual["value"] == {"0": 7}
    assert actual["tags"] == {"0": "tag7"}

    sut.counter(ORDER_CANCELLED, strategy_id, 77, ["tag77"])

    actual = storage_manager.load_data_frame(df_id).to_dict()
    assert len(actual) == 3
    assert "time" in actual
    assert actual["value"] == {"0": 7, "1": 77}
    assert actual["tags"] == {"0": "tag7", "1": "tag77"}


def test_gauge():
    storage_manager = get_storage_manager(
        config=config,
        logger=mock(),
    )
    sut = get_metrics_manager(
        config=config,
        logger=mock(),
        storage_manager=storage_manager,
    )

    strategy_id = "test_strategy"
    df_id = f"Gauge-{ORDER_CANCELLED}-{strategy_id}"

    try:
        storage_manager.delete_data_frame(df_id)
    except Exception:
        pass

    sut.gauge(ORDER_CANCELLED, strategy_id, 8.8, ["tag88"])

    actual = storage_manager.load_data_frame(df_id).to_dict()
    assert len(actual) == 3
    assert "time" in actual
    assert actual["value"] == {"0": 8.8}
    assert actual["tags"] == {"0": "tag88"}

    sut.gauge(ORDER_CANCELLED, strategy_id, 9.9, ["tag99"])

    actual = storage_manager.load_data_frame(df_id).to_dict()
    assert len(actual) == 3
    assert "time" in actual
    assert actual["value"] == {"0": 8.8, "1": 9.9}
    assert actual["tags"] == {"0": "tag88", "1": "tag99"}
