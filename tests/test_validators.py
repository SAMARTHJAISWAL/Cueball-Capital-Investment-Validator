from datetime import datetime
from types import SimpleNamespace as NS

import pytest

from api.utils.validators import find_violations, get_period_bounds


def inv(id, date, amount, sector):
    return NS(id=id, date=datetime.strptime(date, "%Y-%m-%d"), amount=amount, sector=sector)


def rule(amount, time_period=None, sector=None):
    return NS(amount=amount, time_period=time_period, sector=sector)


@pytest.mark.parametrize("date,period,start,end", [
    ("2020-02-29", "Month", "2020-02-01", "2020-03-01"),
    ("2020-12-15", "Month", "2020-12-01", "2021-01-01"),
    ("2020-05-03", "Quarter", "2020-04-01", "2020-07-01"),
    ("2020-11-30", "Quarter", "2020-10-01", "2021-01-01"),
    ("2020-06-01", "Year", "2020-01-01", "2021-01-01"),
])
def test_period_bounds(date, period, start, end):
    d = datetime.strptime(date, "%Y-%m-%d")
    assert get_period_bounds(d, period) == (
        datetime.strptime(start, "%Y-%m-%d"),
        datetime.strptime(end, "%Y-%m-%d"),
    )


def test_unknown_period():
    with pytest.raises(ValueError):
        get_period_bounds(datetime(2020, 1, 1), "Week")


def test_monthly_limit_resets_each_month():
    investments = [inv(1, "2020-01-05", 60, "A"), inv(2, "2020-01-20", 20, "B"), inv(3, "2020-02-01", 60, "A")]
    assert find_violations(investments, [rule(75, "Month")]) == {2}


def test_exactly_at_limit_is_allowed():
    investments = [inv(1, "2020-01-05", 50, "A"), inv(2, "2020-01-06", 25, "A")]
    assert find_violations(investments, [rule(75, "Month")]) == set()


def test_sector_only_rule_is_all_time():
    investments = [inv(1, "2020-01-01", 20, "FinTech"), inv(2, "2023-06-01", 20, "FinTech"), inv(3, "2023-06-02", 99, "SaaS")]
    assert find_violations(investments, [rule(30, sector="FinTech")]) == {2}


def test_sector_and_period_rule_only_counts_that_sector():
    investments = [inv(1, "2020-01-01", 20, "BigData"), inv(2, "2020-02-01", 100, "SaaS"), inv(3, "2020-03-01", 10, "BigData")]
    assert find_violations(investments, [rule(25, "Quarter", "BigData")]) == {3}


def test_chronological_order_not_id_order():
    # ID 1 happens after ID 2, so it is the one that crosses the limit.
    investments = [inv(1, "2020-01-20", 50, "A"), inv(2, "2020-01-10", 50, "A")]
    assert find_violations(investments, [rule(75, "Month")]) == {1}
