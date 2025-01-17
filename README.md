# Cueball Capital Investment Validator

A Flask-based API application that helps Cueball Capital validate investments against their budget rules.

## Budget Rules
The application validates investments against the following types of rules:
1. Monthly investment limits
2. Quarterly investment limits
3. Yearly investment limits
4. Sector-specific investment limits

Rules can be:
- Time-period based (Month/Quarter/Year)
- Sector-specific
- Both time-period and sector-specific


### Technologies Used
- Flask: Web framework
- SQLAlchemy: Database ORM
- Pandas: Data processing
- SQLite: Database

## Testing
To test the APIs, you can use curl commands:
```bash
# Get all budget rules
curl http://127.0.0.1:5000/api/budget_rules

# Get all investments
curl http://127.0.0.1:5000/api/investments

# Get sorted investments
curl "http://127.0.0.1:5000/api/investments?sort=true"

# Get valid investments
curl http://127.0.0.1:5000/api/valid_investments

# Get violating investments
curl http://127.0.0.1:5000/api/violating_investments
```

## Notes
- The time period starts on the 1st of the relevant month
- At least one of Time Period and Sector will be present in a budget rule
- All amounts are in millions of USD
- Date format in investments.csv should be dd/mm/yyyy
