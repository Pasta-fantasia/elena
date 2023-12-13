from test.elena.domain.services.record import Record

from elena.domain.model.trading_pair import TradingPair

expected_limit_min_amount = {
    "function": "limit_min_amount",
    "input": {
        "pair": TradingPair(base="BTC", quote="USDT"),
    },
    "output": 1e-05,
    "time": 1702468422999,
}


def test_deserialize_from_json():
    actual = Record._deserialize_from_json("231213-1702468422999-limit_min_amount.json")
    assert actual == expected_limit_min_amount


def test_load_all_recorded_data():
    actual = Record().load_all_recorded_data()
    assert len(actual) >= 1
    limit_min_amount_data = actual["limit_min_amount"]
    assert len(limit_min_amount_data) >= 1
    for limit_min_amount in limit_min_amount_data:
        if limit_min_amount == expected_limit_min_amount:
            return
    raise AssertionError(
        "Cannot find expected `limit_min_amount` in loaded recorded data."
    )
