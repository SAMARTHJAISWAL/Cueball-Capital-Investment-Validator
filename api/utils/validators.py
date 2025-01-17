from datetime import datetime
from api.models.budget import BudgetRule
from api.models.investment import Investment

def get_period_bounds(date, period):
    if period == 'Month':
        start_date = date.replace(day=1)
        next_month = date.month + 1 if date.month < 12 else 1
        next_year = date.year + 1 if date.month == 12 else date.year
        end_date = datetime(next_year, next_month, 1)
    elif period == 'Quarter':
        quarter = (date.month - 1) // 3
        start_date = datetime(date.year, quarter * 3 + 1, 1)
        end_month = (quarter + 1) * 3 + 1
        end_year = date.year + 1 if end_month > 12 else date.year
        end_month = end_month if end_month <= 12 else 1
        end_date = datetime(end_year, end_month, 1)
    else:
        start_date = datetime(date.year, 1, 1)
        end_date = datetime(date.year + 1, 1, 1)
    return start_date, end_date

def check_budget_violation(investment):
    rules = BudgetRule.query.all()
    
    for rule in rules:
        if rule.sector and rule.sector != investment.sector:
            continue
            
        if rule.time_period:
            start_date, end_date = get_period_bounds(investment.date, rule.time_period)
            
            period_investments = Investment.query.filter(
                Investment.date >= start_date,
                Investment.date < end_date,
                Investment.id <= investment.id
            ).all()
            
            if rule.sector:
                period_investments = [
                    inv for inv in period_investments 
                    if inv.sector == rule.sector
                ]
            
            period_total = sum(inv.amount for inv in period_investments)
            
            if period_total > rule.amount:
                return True
                
    return False