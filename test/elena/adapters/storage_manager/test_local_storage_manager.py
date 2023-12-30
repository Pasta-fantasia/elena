import pathlib
from os import path

from mockito import mock

from elena.adapters.storage_manager.local_storage_manager import \
    LocalStorageManager
from elena.domain.model.bot_status import BotStatus
from elena.domain.model.order import Order, OrderSide, OrderType
from elena.domain.model.trading_pair import TradingPair


def test_load_bot_status():
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
    config = {
        "home": path.join(pathlib.Path(__file__).parent.parent.parent.parent, "test_home"),
        "StorageManager": {"path": "storage"},
    }
    sut.init(
        config=config,
        logger=mock(),
    )
    sut.save_bot_status(bot_status)

    actual = sut.load_bot_status(bot_status.bot_id)
    assert actual == bot_status
