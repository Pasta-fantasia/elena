# TODO

## orders

createLimitBuyOrder(amount, price ) # buy (0.01 BTC at 47k USDT)  pair=BTC/UST
createLimitSellOrder(amount, price )

createMarketBuyOrder(amount)
createMarketSellOrder(amount)

## Why?


## Exceptions


## Trades, how to implement them

## ExchangeManager and CctxExchangeManager
- ExchangeType read from ccxt.exchanges

- fetch_order() OK,  but we may want to get all the orders at once, at least at bot level.


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

