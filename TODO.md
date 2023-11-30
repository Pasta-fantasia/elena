# TODO

## Pere

### Bot

A bot runs a strategy on an exchange for a pair, based on bot configuration
Has to be able to call all the exchange operations directly, without calling the ExchangeManager
Will be an abstract class with the following properties and methods:

#### Properties

- id: str
- name: str
- pair: TradingPair
- config: Dict
- limits                  // value limits when placing orders on this market
  - fields
    - amount
        - min: 0.01,      // order amount should be > min
        - max: 1000,      // order amount should be < max
    - price
        - min: 0.01,      // order price should be > min
        - max: 1000,      // order price should be < max
    - cost                // order cost = price * amount
        - min: 0.01,      // order cost should be > min
        - max: 1000,      // order cost should be < max
    - leverage
        - min: 0.01,      // order leverage should be > min
        - max: 1000,      // order leverage should be < max
  - create it as a data class, not a dict
  - example of usage: `self.limit.amount.max * 22`


#### Methods

Methods don't raise exceptions, they return None if they fail

- cancel_order(order_id: str) -> t.Optional[Order]
- get_balance() -> t.Optional[Balance]
- stop_loss(amount: float, stop_price: float, price: float) -> t.Optional[Order]
- read_candles(
          limt:int, # Page size
          time_frame: TimeFrame = self.bot_config.time_frame
      ) -> t.Optional[pd.DataFrame]
- get_order_book() -> t.Optional[OrderBook]
- createLimitBuyOrder(amount, price ) -> t.Optional[Order] # buy (0.01 BTC at 47k USDT)  pair=BTC/UST
- createLimitSellOrder(amount, price ) -> t.Optional[Order]
- createMarketBuyOrder(amount) -> t.Optional[Order]
- createMarketSellOrder(amount) -> t.Optional[Order]
- fetch_order() -> t.Optional[Order]
 
#### Implementation notes

- call to amount_to_precision & price_to_precision before calling exchange
- capture all errors, log it and return None if they fail


## orders

createLimitBuyOrder(amount, price ) # buy (0.01 BTC at 47k USDT)  pair=BTC/UST
createLimitSellOrder(amount, price )

createMarketBuyOrder(amount)
createMarketSellOrder(amount)

## Why?
```
class ExchangeManager(Protocol):

    def read_candles(
            self,
            exchange: Exchange,
``` 
If it's an ExchangeMANAGER is it not enough to initialize it with an Exchange instance? Why a protocol? We may want ot have a multi exchange strategy but maybe on v3


## Exceptions


## Trades, how to implement them



## CctxExchangeManager
- do we need it?
- Implement
  - ExchangeManager.amount_to_precision
  - ExchangeManager.price_to_precision

## ExchangeManager and CctxExchangeManager
- _fetch_candles needs how the limit parameter... and _fetch_candles_with_retry may paginate to get that limit. 
- _connect_mapper: auto add others? This way if a user want to use Coinbase he/she needs to change elena's code
- Exchange.ExchangeType looks like a type but we can only have one at a single time, check StrategyManagerImpl(StrategyManager)
  ``` def get_exchange(self, exchange_id: ExchangeType) -> Exchange:
        for exchange in self._exchanges:
            if exchange.id == exchange_id.value:
                return exchange```
- expose active, limits, taker/maker fees (and percentage)  check bellow
- fetch_order() OK,  but we may want to get all the orders at once, at least at bot level.

## ExchangeManager(Protocol)

While 
```
def read_candles(
            self,
            exchange: Exchange,
            pair: TradingPair,
            time_frame: TimeFrame = TimeFrame.min_1
    ) -> pd.DataFrame:
```

Then:
``` 
    def place_order(
            self,
            exchange: Exchange,
            bot_config: BotConfig,
```
*bot_config: BotConfig,???* It makes Strategies too complex.


## Model.BotConfig
- Found but not sure how wrote it: config: Dict  # TODO Transform to data class


## Service.StrategyManagerImpl
- StrategyManagerImpl.run: check if the cron expression before running the bot
  - https://pypi.org/project/cron-converter/
  - but should be implemented in a way that a Strategy can evaluate cron expressions too for certain actions... like utils.cron_checker( cron_expression, last_execution ) -> Bool True si ya ha "caducado" 
- _update_orders_status: Full review, check TODOs on code and think about the relationship with trades and notifications

## StrategyManager(Protocol)

This protocol defines stop_loss_limit, get_balance, read_candles... methods... but are this in the right place? I would place it on ExchangeManager only... no?


## class Trade(BaseModel)
- Make the maths to know if we're earning, duration / return_pct
- Check: A TradeManager should be created to implement .open_trade()... right?


## amount_to_precision / price_to_precision

```
symbol = 'BTC/USDT'
amount = 1.2345678  # amount in base currency BTC
price = 87654.321  # price in quote currency USDT
formatted_amount = exchange.amount_to_precision(symbol, amount)
formatted_price = exchange.price_to_precision(symbol, price)
print(formatted_amount, formatted_price)

1.23456 87654.32
```

## expose active, limits, taker/maker fees (and percentage) 

If it's easy expose all

https://github.com/ccxt/ccxt/wiki/Manual#market-structure
markets = exchange.load_markets()
or exchange.markets after call exchange.load_markets()

```
{
    'id':      'btcusd',      // string literal for referencing within an exchange
    'symbol':  'BTC/USD',     // uppercase string literal of a pair of currencies
    'base':    'BTC',         // uppercase string, unified base currency code, 3 or more letters
    'quote':   'USD',         // uppercase string, unified quote currency code, 3 or more letters
    'baseId':  'btc',         // any string, exchange-specific base currency id
    'quoteId': 'usd',         // any string, exchange-specific quote currency id
    'active':   true,         // boolean, market status
    'type':    'spot',        // spot for spot, future for expiry futures, swap for perpetual swaps, 'option' for options
    'spot':     true,         // whether the market is a spot market
    'margin':   true,         // whether the market is a margin market
    'future':   false,        // whether the market is a expiring future
    'swap':     false,        // whether the market is a perpetual swap
    'option':   false,        // whether the market is an option contract
    'contract': false,        // whether the market is a future, a perpetual swap, or an option
    'settle':   'USDT',       // the unified currency code that the contract will settle in, only set if `contract` is true
    'settleId': 'usdt',       // the currencyId of that the contract will settle in, only set if `contract` is true
    'contractSize': 1,        // the size of one contract, only used if `contract` is true
    'linear':   true,         // the contract is a linear contract (settled in quote currency)
    'inverse':  false,        // the contract is an inverse contract (settled in base currency)
    'expiry':  1641370465121, // the unix expiry timestamp in milliseconds, undefined for everything except market['type'] `future`
    'expiryDatetime': '2022-03-26T00:00:00.000Z', // The datetime contract will in iso8601 format
    'strike': 4000,           // price at which a put or call option can be exercised
    'optionType': 'call',     // call or put string, call option represents an option with the right to buy and put an option with the right to sell
    'taker':    0.002,        // taker fee rate, 0.002 = 0.2%
    'maker':    0.0016,       // maker fee rate, 0.0016 = 0.16%
    'percentage': true,       // whether the taker and maker fee rate is a multiplier or a fixed flat amount
    'tierBased': false,       // whether the fee depends on your trading tier (your trading volume)
    'feeSide': 'get',         // string literal can be 'get', 'give', 'base', 'quote', 'other'
    'precision': {            // number of decimal digits "after the dot"
        'price': 8,           // integer or float for TICK_SIZE roundingMode, might be missing if not supplied by the exchange
        'amount': 8,          // integer, might be missing if not supplied by the exchange
        'cost': 8,            // integer, very few exchanges actually have it
    },
    'limits': {               // value limits when placing orders on this market
        'amount': {
            'min': 0.01,      // order amount should be > min
            'max': 1000,      // order amount should be < max
        },
        'price': { ... },     // same min/max limits for the price of the order
        'cost':  { ... },     // same limits for order cost = price * amount
        'leverage': { ... },  // same min/max limits for the leverage of the order
    },
    'info':      { ... },     // the original unparsed market info from the exchange
}

```

