from pydantic import BaseModel


class BotBudget(BaseModel):
    # Budget expressed on quote to spend in the strategy.
    set_limit: float = 0.0  # Limit set on the bot configuration.
    current_limit: float = 0.0  # Limit to use now, if profit is taken this number will increase over set_limit.
    used: float = 0.0  # Budget currently used
    pct_reinvest_profit: float = 100.0  # set how much to re-invest en percentage.

    def set(self, budget: float):
        # Every time a set comes with a new value the budget is changed
        # No matter if there are accumulated profit.
        # While the user kept the same budget on the bot configuration
        # the current_limit can use the profit.
        if self.set_limit != budget:
            self.set_limit = budget
            self.current_limit = budget

    def lock(self, locked: float):
        if self.is_budget_limited and self.free > locked:
            # TODO: raise? return false? as it is now the operation is already done...
            pass
        self.used = round(self.used + locked, 8)

    def unlock(self, released: float, rtn: float):
        if self.is_budget_limited and self.used > released:
            # TODO: think!
            pass
        # TODO profit control in budget
        released_without_profit = released - rtn
        self.used = round(self.used - released_without_profit, 8)

        re_usable_profit = rtn
        if self.pct_reinvest_profit != 100.0 and rtn > 0.0:
            re_usable_profit = rtn * (self.pct_reinvest_profit / 100)

        self.current_limit = round(self.current_limit + re_usable_profit, 8)

    @property
    def free(self) -> float:
        return round(self.current_limit - self.used, 8)

    @property
    def is_budget_limited(self) -> bool:
        return self.set_limit > 0.0

    @property
    def total(self) -> float:
        return round(self.free + self.used, 8)
