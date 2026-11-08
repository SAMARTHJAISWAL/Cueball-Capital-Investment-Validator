"""Budget rule validation.

Investments are processed in chronological order (date, then ID). For every rule
that applies to an investment, we total that investment plus all earlier ones in
the same rule scope:

* time-period rules (Month / Quarter / Year) only count investments in the same
  calendar period, starting on the 1st of the month;
* sector rules only count investments in that sector;
* a sector rule without a time period caps the sector's all-time total.

If any such total exceeds the rule's amount, the investment violates the budget.
Violating investments still count toward later totals.
"""
from datetime import datetime
from typing import Iterable, Optional, Set, Tuple

PERIODS = ("Month", "Quarter", "Year")


def get_period_bounds(date: datetime, period: str) -> Tuple[datetime, datetime]:
    """Return [start, end) of the calendar Month / Quarter / Year containing `date`."""
    if period == "Month":
        start = datetime(date.year, date.month, 1)
    elif period == "Quarter":
        start = datetime(date.year, (date.month - 1) // 3 * 3 + 1, 1)
    elif period == "Year":
        start = datetime(date.year, 1, 1)
    else:
        raise ValueError(f"Unknown time period: {period!r}")

    months = {"Month": 1, "Quarter": 3, "Year": 12}[period]
    month_index = start.month - 1 + months
    end = datetime(start.year + month_index // 12, month_index % 12 + 1, 1)
    return start, end


def _order_key(inv):
    return (inv.date, inv.id)


def _in_scope(rule, inv, period_bounds: Optional[Tuple[datetime, datetime]]) -> bool:
    if rule.sector and inv.sector != rule.sector:
        return False
    if period_bounds is not None:
        start, end = period_bounds
        if not (start <= inv.date < end):
            return False
    return True


def violates(investment, rules: Iterable, investments: Iterable) -> bool:
    """True if `investment` pushes any applicable rule's running total over its amount."""
    investments = list(investments)
    for rule in rules:
        if rule.sector and rule.sector != investment.sector:
            continue
        bounds = get_period_bounds(investment.date, rule.time_period) if rule.time_period else None
        total = sum(
            inv.amount
            for inv in investments
            if _order_key(inv) <= _order_key(investment) and _in_scope(rule, inv, bounds)
        )
        if total > rule.amount:
            return True
    return False


def find_violations(investments: Iterable, rules: Iterable) -> Set[int]:
    """IDs of all investments that violate at least one budget rule."""
    investments = list(investments)
    rules = list(rules)
    return {inv.id for inv in investments if violates(inv, rules, investments)}


def check_budget_violation(investment) -> bool:
    """Database-backed check for a single investment (kept for backwards compatibility)."""
    from api.models.budget import BudgetRule
    from api.models.investment import Investment

    return violates(investment, BudgetRule.query.all(), Investment.query.all())
