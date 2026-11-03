# Cueball Capital Investment Validator

[![tests](https://github.com/SAMARTHJAISWAL/Cueball-Capital-Investment-Validator/actions/workflows/tests.yml/badge.svg)](https://github.com/SAMARTHJAISWAL/Cueball-Capital-Investment-Validator/actions/workflows/tests.yml)

A Flask API that checks Cueball Capital's investments against its budget rules. On first start it loads `data/budget.csv` and `data/investments.csv` into SQLite, then exposes endpoints listing the rules, all investments, and which investments are within budget and which violate it.

## Budget rules

Each rule has an amount (in millions of USD) and at least one of a time period or a sector:

| Rule type | Example (`data/budget.csv`) | Meaning |
|-----------|-----------------------------|---------|
| Time period only | `75, Month` | At most 75 per calendar month across all sectors |
| Sector only | `30, , FinTech` | At most 30 in FinTech in total (all time) |
| Time period + sector | `25, Quarter, BigData` | At most 25 in BigData per calendar quarter |

How validation works:

- Investments are processed in date order (ties broken by ID).
- For each rule that applies to an investment, the investment's amount is added to all earlier investments in the same scope (same calendar month/quarter/year starting on the 1st, and/or same sector).
- If any total goes **over** the rule amount, the investment violates the budget. Hitting the limit exactly is allowed.
- Violating investments still count toward later totals.

With the sample data, investments 1, 2 and 9 are valid and 3, 4, 5, 6, 7, 8 and 10 violate.

## Tech stack

Python 3.10+, Flask 3, Flask-SQLAlchemy / SQLAlchemy 2, SQLite, pandas (CSV loading), pytest.

## Setup

```bash
git clone https://github.com/SAMARTHJAISWAL/Cueball-Capital-Investment-Validator.git
cd Cueball-Capital-Investment-Validator
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # optional
python run.py
```

The API runs at <http://127.0.0.1:5000>. On macOS, port 5000 is often taken by AirPlay Receiver; run `PORT=5001 python run.py` instead.

The SQLite database is created in `instance/cueball.db` and filled from the CSVs only when it is empty. Delete it to reload after editing the CSVs.

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///cueball.db` | SQLAlchemy URL. Relative SQLite paths go in `instance/` |
| `BUDGET_CSV` | `data/budget.csv` | Budget rules file (`ID,Amount,Time Period,Sector`) |
| `INVESTMENTS_CSV` | `data/investments.csv` | Investments file (`ID,Date,Amount,Sector`, dates `dd/mm/yyyy`) |
| `HOST` / `PORT` | `127.0.0.1` / `5000` | Bind address |
| `FLASK_DEBUG` | `0` | `1` enables debug mode |
| `SECRET_KEY` | `dev` | Flask secret key (no sessions are used today) |

## API

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Service info and endpoint list |
| `GET` | `/api/budget_rules` | All budget rules |
| `GET` | `/api/investments` | All investments by ID; `?sort=true` orders them by date |
| `GET` | `/api/valid_investments` | Investments that break no rule (date order) |
| `GET` | `/api/violating_investments` | Investments that break at least one rule (date order) |

```bash
curl http://127.0.0.1:5000/api/budget_rules
curl "http://127.0.0.1:5000/api/investments?sort=true"
curl http://127.0.0.1:5000/api/valid_investments
curl http://127.0.0.1:5000/api/violating_investments
```

Example investment:

```json
{"id": 1, "date": "06/01/2020", "amount": 10.0, "sector": "BigData"}
```

## Project structure

```
app.py                       # app factory, DB init and CSV loading
run.py                       # entry point
config/config.py             # settings from env / .env
api/models/                  # BudgetRule, Investment (SQLAlchemy)
api/routes/                  # budget and investment endpoints
api/utils/validators.py      # budget rule logic (pure functions)
data/                        # sample budget.csv and investments.csv
tests/                       # pytest suite
```

## Tests

```bash
pip install -r requirements-dev.txt
python -m pytest
```

The validator tests use plain objects. The route tests load the sample CSVs into a temporary SQLite database.
