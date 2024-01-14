from elena.domain.model.bot_status import BotBudget


def test_budget_simple():
    budget = BotBudget()

    # verify default values
    assert budget.pct_reinvest_profit == 100.0
    assert budget.free == 0
    assert budget.used == 0
    assert budget.total == 0
    assert budget.current_limit == 0

    # check set
    budget.set(10)
    assert budget.current_limit == 10
    assert budget.set_limit == 10
    assert budget.is_budget_limited

    # check lock
    budget.lock(8)
    assert budget.free == 2
    assert budget.used == 8
    assert budget.total == 10

    # check unlock whit profit handling with default budget.pct_re_invest_profit = 100
    budget.unlock(10, 2)

    assert budget.free == 12
    assert budget.used == 0

    # check new set without used balance
    budget.set(100)
    assert budget.set_limit == 100
    assert budget.free == 100
    assert budget.used == 0


def test_budget_partial_unlock_with_100_benefits():
    budget = BotBudget()
    budget.set(100)
    budget.lock(100)  # buy 100

    assert budget.pct_reinvest_profit == 100.0
    assert budget.set_limit == 100
    assert budget.used == 100

    budget.unlock(100, 50)  # sell 50, but with 50 in benefits, take all as new budget
    assert budget.set_limit == 100
    assert budget.free == 100
    assert budget.used == 50
    assert budget.total == 150
    assert budget.current_limit == 150


def test_budget_partial_unlock_with_50_benefits():
    budget = BotBudget()
    budget.set(100)
    budget.lock(100)  # buy 100
    budget.pct_reinvest_profit = 50.0

    assert budget.pct_reinvest_profit == 50.0
    assert budget.set_limit == 100
    assert budget.used == 100

    budget.unlock(100, 50)  # sell 50, but with 50 in benefits, take half as more budget
    assert budget.set_limit == 100
    assert budget.free == 75
    assert budget.used == 50
    assert budget.total == 125
    assert budget.current_limit == 125


def test_budget_partial_unlock_with_0_benefits():
    budget = BotBudget()
    budget.set(100)
    budget.lock(100)  # buy 100
    budget.pct_reinvest_profit = 0

    assert budget.pct_reinvest_profit == 0
    assert budget.set_limit == 100
    assert budget.used == 100

    budget.unlock(100, 50)  # sell 50, but with 50 in benefits, take none as more budget
    assert budget.set_limit == 100
    assert budget.free == 50
    assert budget.used == 50
    assert budget.total == 100
    assert budget.current_limit == 100


def test_budget_on_a_new_set_with_used_budget():
    budget = BotBudget()
    budget.set(100)
    budget.lock(100)  # buy 100
    budget.pct_reinvest_profit = 0

    budget.unlock(100, 50)  # sell 50, but with 50 in benefits, take none as more budget
    assert budget.set_limit == 100
    assert budget.free == 50
    assert budget.used == 50
    assert budget.total == 100
    assert budget.current_limit == 100

    budget.set(200)  # change budget up
    assert budget.set_limit == 200
    assert budget.free == 150
    assert budget.used == 50
    assert budget.total == 200
    assert budget.current_limit == 200
    assert budget.pct_reinvest_profit == 0

    budget.set(25)  # change budget down
    assert budget.set_limit == 25
    assert budget.free == -25
    assert budget.used == 50
    assert budget.total == 25
    assert budget.current_limit == 25
    assert budget.pct_reinvest_profit == 0
