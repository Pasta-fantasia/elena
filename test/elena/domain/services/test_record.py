from test.elena.domain.services.record import Record

from elena.domain.model.trading_pair import TradingPair

expected_limit_min_amount = {
    "function": "limit_min_amount",
    "input": {
        "pair": TradingPair(base="BTC", quote="USDT"),
    },
    "output": 1e-05,
}


def test_deserialize_from_json():
    actual = Record._deserialize_from_json("limit_min_amount-1705236507196.json")
    assert actual == expected_limit_min_amount


def test_load_all_recorded_data():
    actual = Record().load_all_recorded_data()
    assert len(actual) >= 1
    limit_min_amount_data = actual["limit_min_amount"]
    assert len(limit_min_amount_data) >= 1
    for limit_min_amount in limit_min_amount_data:
        if limit_min_amount == expected_limit_min_amount:
            return
    raise AssertionError("Cannot find expected `limit_min_amount` in loaded recorded data.")


def test_load_recorded_output():
    all_recorded_data = Record().load_all_recorded_data()
    actual = Record().load_recorded_output(
        "amount_to_precision",
        all_recorded_data,
        pair=TradingPair(base="BTC", quote="USDT"),
        amount=0.00711286679281143,
    )
    assert actual == 0.00711
