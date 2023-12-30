import pathlib
from os import path

from mockito import mock
from pandas import DataFrame

from elena.adapters.storage_manager.local_storage_manager import \
    LocalStorageManager
from elena.domain.model.bot_status import BotStatus
from elena.domain.model.order import Order, OrderSide, OrderType
from elena.domain.model.trading_pair import TradingPair


def test_save_and_load_bot_status():
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
    )

    sut = LocalStorageManager()
    sut.init(
        config={
            "home": path.join(pathlib.Path(__file__).parent.parent.parent.parent, "test_home"),
            "StorageManager": {"path": "storage"},
        },
        logger=mock(),
    )
    sut.save_bot_status(bot_status)

    actual = sut.load_bot_status(bot_status.bot_id)
    assert actual == bot_status


def test_save_and_load_data_frame():
    df_dict = {
        "Name": {
            0: "Person_1",
            1: "Person_2",
            2: "Person_3",
            3: "Person_4",
            4: "Person_5",
            5: "Person_6",
            6: "Person_7",
            7: "Person_8",
            8: "Person_9",
            9: "Person_10",
        },
        "Age": {
            0: 56,
            1: 46,
            2: 32,
            3: 25,
            4: 38,
            5: 56,
            6: 36,
            7: 40,
            8: 28,
            9: 28,
        },
        "City": {
            0: "City_A",
            1: "City_B",
            2: "City_C",
            3: "City_A",
            4: "City_B",
            5: "City_C",
            6: "City_A",
            7: "City_B",
            8: "City_C",
            9: "City_A",
        },
    }
    df = DataFrame.from_dict(df_dict)

    sut = LocalStorageManager()
    sut.init(
        config={
            "home": path.join(pathlib.Path(__file__).parent.parent.parent.parent, "test_home"),
            "StorageManager": {"path": "storage"},
        },
        logger=mock(),
    )
    sut.save_data_frame("test_df_id", df)

    actual = sut.load_data_frame("test_df_id")
    assert actual.to_dict() == df_dict
