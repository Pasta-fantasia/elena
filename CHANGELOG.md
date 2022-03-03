# 1.6.0
- Sell recalculates after a timeout. Sell at higher price or stop loss #36
- Algo 10 - buy on bid sell at fixed margin #37

# 1.5.3
- Rename Auto cancel parameter in .json

# 1.5.2
- Auto cancel parameter in .json
- Log error connection
- Default values on _read_state

# 1.5.1
- Type Error

# 1.5 
- Reinvest benefit parameter #27
- Try to minimize time to buy 
  - Don't estimate buy, buy at lowest bid on the order book #31
    - New algos 8,9 and algo migration for 4->7 to 8 and 9.
  - Buy order auto cancellation #14
  - Decrease sleep times.
  - Buy and sell can occur in a single iteration. Reducing time to buy causes that a buy order are executed immediately.
- minimum_profit=1.005
- More details for: Status in active .jsons #16

# 1.4
- Only create orders above or upper the current price #17
- Status in active .jsons #16

# 1.3 New algos and order details on history jsons
- New algos 6, 7.
- Refactor algo for better understanding.
- _save_history_state_and_profit: saves buy and sell orders details, iteration_benefit, iteration_margin and left_on_asset into the history .json
- _delete_state if the state is not active when the cycle is over "delete it" (it actually renames it to .inactive)
- Some TODOs

# 1.2 Refactor and testing first iteration
- Refactor Exchange class. [#2](https://github.com/Ciskam-Lab/elena/issues/2) [#9](https://github.com/Ciskam-Lab/elena/issues/9)
- Exchange class public method should not uses Binance directly. [#3](https://github.com/Ciskam-Lab/elena/issues/3) [#10](https://github.com/Ciskam-Lab/elena/issues/10) 
- Create Elena Class. [#4](https://github.com/Ciskam-Lab/elena/issues/4) [#11](https://github.com/Ciskam-Lab/elena/issues/11) 
- Test data recorder.

# 1.1
- New algorithms (3,4,5)
- Exchange 
  - buy with less balance than max_order
  - cache symbol_info with lru_cache
  - TODOs
- Logging multiple parameters
- Enum OrderStatus
- Refactor private methods
- check_order_status

# 1.0
Initial version