from test.elena.domain.services.record import Record

from elena.domain.model.trading_pair import TradingPair


def test_deserialize_from_json():
    actual = Record.deserialize_from_json("231213-1702448057597-limit_min_amount.json")
    assert actual == {
        "function": "limit_min_amount",
        "input": {
            "args": TradingPair(
                base="BTC",
                quote="USDT",
            ),
            "kwargs": [],
        },
        "output": 1e-05,
        "time": 1702448057597,
    }
