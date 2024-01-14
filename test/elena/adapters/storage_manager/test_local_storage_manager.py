import pathlib
from os import path

import pandas as pd
from mockito import mock
from pandas import DataFrame

from elena.domain.model.bot_status import BotStatus, BotBudget
from elena.domain.model.order import Order, OrderSide, OrderType
from elena.domain.model.trading_pair import TradingPair
from elena.domain.services.elena import get_storage_manager


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
        budget=BotBudget(),
    )

    sut = get_storage_manager(
        config={
            "home": path.join(pathlib.Path(__file__).parent.parent.parent.parent, "test_home"),
            "StorageManager": {
                "class": "elena.adapters.storage_manager.local_storage_manager.LocalStorageManager",
                "path": "storage",
            },
        },
        logger=mock(),
    )
    sut.save_bot_status(bot_status)

    actual = sut.load_bot_status(bot_status.bot_id)
    assert actual == bot_status


def test_save_and_load_data_frame():
    data = {
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
    df = DataFrame(data)

    sut = get_storage_manager(
        config={
            "home": path.join(pathlib.Path(__file__).parent.parent.parent.parent, "test_home"),
            "StorageManager": {
                "class": "elena.adapters.storage_manager.local_storage_manager.LocalStorageManager",
                "path": "storage",
            },
        },
        logger=mock(),
    )
    sut.save_data_frame("test_df_id", df)

    actual = sut.load_data_frame("test_df_id")
    actual.to_dict() == df.to_dict()


def test_merge_data_frame_using_candles():
    existing_df = pd.DataFrame(
        {
            "Open time": {
                0: 1702479180000,
                1: 1702479240000,
                2: 1702479300000,
                3: 1702479360000,
                4: 1702479420000,
                5: 1702479480000,
            },
            "Open": {
                0: 41372.11111,
                1: 41350.22222,
                2: 41353.33333,
                3: 41357.44444,
                4: 41345.55555,  # This value should be overwritten
                5: 41374.66666,  # This value should be overwritten
            },
            "High": {
                0: 41381.04,
                1: 41353.37,
                2: 41357.35,
                3: 41357.66,
                4: 41378.94,
                5: 41378.8,
            },
            "Low": {
                0: 41354.07,
                1: 41339.94,
                2: 41345.76,
                3: 41345.54,
                4: 40757.6,
                5: 41371.49,
            },
            "Close": {
                0: 41354.07,
                1: 41353.37,
                2: 41357.35,
                3: 41347.93,
                4: 41378.86,
                5: 41371.49,
            },
            "Volume": {
                0: 0.3119400144,
                1: 0.3297800124,
                2: 0.2395299971,
                3: 0.1104699969,
                4: 0.7769600153,
                5: 0.1653700024,
            },
        }
    )

    df_to_be_merged = pd.DataFrame(
        {
            "Open time": {
                0: 1702479420000,
                1: 1702479480000,
                2: 1702479540000,
                3: 1702479600000,
                4: 1702479660000,
                5: 1702479720000,
            },
            "Open": {
                0: 41345.77777,  # This value has changed
                1: 41374.88888,  # This value has changed
                2: 41371.99999,
                3: 41369.10101,
                4: 41352.11111,
                5: 41375.12121,
            },
            "High": {
                0: 41378.94,
                1: 41378.8,
                2: 41378.5,
                3: 41369.79,
                4: 41375.0,
                5: 41392.71,
            },
            "Low": {
                0: 40757.6,
                1: 41371.49,
                2: 41364.81,
                3: 41345.44,
                4: 41352.15,
                5: 41375.0,
            },
            "Close": {
                0: 41378.86,
                1: 41371.49,
                2: 41369.0,
                3: 41350.59,
                4: 41375.0,
                5: 41392.71,
            },
            "Volume": {
                0: 0.7769600153,
                1: 0.1653700024,
                2: 0.2307499945,
                3: 0.3550100029,
                4: 0.3790900111,
                5: 0.1978600025,
            },
        }
    )

    expected_df = pd.DataFrame(
        {
            "Open time": {
                0: 1702479180000,
                1: 1702479240000,
                2: 1702479300000,
                3: 1702479360000,
                4: 1702479420000,
                5: 1702479480000,
                6: 1702479540000,
                7: 1702479600000,
                8: 1702479660000,
                9: 1702479720000,
            },
            "Open": {
                0: 41372.11111,
                1: 41350.22222,
                2: 41353.33333,
                3: 41357.44444,
                4: 41345.77777,  # Overwrote value
                5: 41374.88888,  # Overwrote value
                6: 41371.99999,
                7: 41369.10101,
                8: 41352.11111,
                9: 41375.12121,
            },
            "High": {
                0: 41381.04,
                1: 41353.37,
                2: 41357.35,
                3: 41357.66,
                4: 41378.94,
                5: 41378.8,
                6: 41378.5,
                7: 41369.79,
                8: 41375.0,
                9: 41392.71,
            },
            "Low": {
                0: 41354.07,
                1: 41339.94,
                2: 41345.76,
                3: 41345.54,
                4: 40757.6,
                5: 41371.49,
                6: 41364.81,
                7: 41345.44,
                8: 41352.15,
                9: 41375.0,
            },
            "Close": {
                0: 41354.07,
                1: 41353.37,
                2: 41357.35,
                3: 41347.93,
                4: 41378.86,
                5: 41371.49,
                6: 41369.0,
                7: 41350.59,
                8: 41375.0,
                9: 41392.71,
            },
            "Volume": {
                0: 0.3119400144,
                1: 0.3297800124,
                2: 0.2395299971,
                3: 0.1104699969,
                4: 0.7769600153,
                5: 0.1653700024,
                6: 0.2307499945,
                7: 0.3550100029,
                8: 0.3790900111,
                9: 0.1978600025,
            },
        }
    )

    sut = get_storage_manager(
        config={
            "home": path.join(pathlib.Path(__file__).parent.parent.parent.parent, "test_home"),
            "StorageManager": {
                "class": "elena.adapters.storage_manager.local_storage_manager.LocalStorageManager",
                "path": "storage",
            },
        },
        logger=mock(),
    )
    sut.save_data_frame("test_df_id", existing_df)
    actual = sut.merge_data_frame("test_df_id", df_to_be_merged, "Open time")

    actual.to_dict() == expected_df.to_dict()
