# Changelog

## 2.3.3
- fix: Amount to close is insufficient for trade #75
- test: tests and test data
- fix: lint rules

## 2.3.2
- fix: stop loss notification message
- doc: changelog

## 2.3.1
- Send benefit and stop close count as metric

## 2.3.0
- Merge from /main
- refactor: BotStatusLogic
- style: more detail in errors
- feat: Store metrics in jsonl

## 2.2.9
- fix: force never use or store candles
- fix: stop loss notification message 
- fix: preparation for other exchanges, not ready
- fix: get_estimated_last_close can get empty asks/bids -> don't log error but still return None
- fix: error messages

## 2.2.2
- Notifications
- Metrics
- Storage Abstraction
- Trade, orders and budget control
- Testing
- Github actions
- Lint and pre-commit

## 2.1.0
- Dynamic instance of Strategy
- Log rotation
- Minor bugs

## 2.0.0
- New hexagonal architecture

## 1.6.3
- Fix double _self._update_orders_status_values_and_profits()_
- Add _status == OrderStatus.EXPIRED.value_ as cancellation reason. #lunagate

## 1.6.2
- Fix runtime error due to lack of test data recorder notation import
- Fix test_get_candles()
- Rename Exchange to ExchangeManager
- Create Exchange port to prepare Exchange abstraction layer with hexagonal architecture
- Convert Binance into an adapter implementing Exchange port

## 1.6.1
- Force buy price for _Don't estimate buy, buy at lowest bid on the order book_ #31
- Convert to BUSD: Status in active .jsons #16
- Migrate any bot to new algos and default buy_auto_cancel_timeout, sell_auto_cancel_timeout and sell_auto_cancel_im_feeling_lucky_data_samples
- Verify only one instance of elena.sh

## 1.6.0
- Sell recalculates after a timeout. Sell at higher price or stop loss #36
- Algo 10 - buy on bid sell at fixed margin #37
- sleep_until_factor parameter 

## 1.5.3
- Rename Auto cancel_order parameter in .json

## 1.5.2

- Auto cancel_order parameter in .json
- Log error connection
- Default values on _read_state

## 1.5.1
- Type Error

## 1.5 
- Reinvest benefit parameter #27
- Try to minimize time to buy 
  - Don't estimate buy, buy at lowest bid on the order book #31
    - New algos 8,9 and algo migration for 4->7 to 8 and 9.
  - Buy order auto cancellation #14
  - Decrease sleep times.
  - Buy and sell can occur in a single iteration. Reducing time to buy causes that a buy order are executed immediately.
- minimum_profit=1.005
- More details for: Status in active .jsons #16

## 1.4
- Only create orders above or upper the current price #17
- Status in active .jsons #16

## 1.3 New algos and order details on history jsons
- New algos 6, 7.
- Refactor algo for better understanding.
- _save_history_state_and_profit: saves buy and sell orders details, iteration_benefit, iteration_margin and left_on_asset into the history .json
- _delete_state if the state is not active when the cycle is over "delete it" (it actually renames it to .inactive)
- Some TODOs

## 1.2 Refactor and testing first iteration
- Refactor Exchange class. [#2](https://github.com/Ciskam-Lab/elena/issues/2) [#9](https://github.com/Ciskam-Lab/elena/issues/9)
- Exchange class public method should not uses Binance directly. [#3](https://github.com/Ciskam-Lab/elena/issues/3) [#10](https://github.com/Ciskam-Lab/elena/issues/10) 
- Create Elena Class. [#4](https://github.com/Ciskam-Lab/elena/issues/4) [#11](https://github.com/Ciskam-Lab/elena/issues/11) 
- Test data recorder.

## 1.1
- New algorithms (3,4,5)
- Exchange 
  - buy with less balance than max_order
  - cache symbol_info with lru_cache
  - TODOs
- Logging multiple parameters
- Enum OrderStatus
- Refactor private methods
- check_order_status

## 1.0
Initial version