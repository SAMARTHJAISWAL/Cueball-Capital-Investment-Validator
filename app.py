from datetime import datetime

import pandas as pd
from flask import Flask, jsonify

from api.models.budget import BudgetRule
from api.models.investment import Investment
from api.routes.budget_routes import budget_bp
from api.routes.investment_routes import investment_bp
from api.utils.database import db
from config.config import Config


def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)

    app.register_blueprint(budget_bp)
    app.register_blueprint(investment_bp)

    @app.route("/")
    def home():
        return jsonify({
            "message": "Welcome to Cueball Capital Investment API",
            "endpoints": {
                "Budget Rules": "/api/budget_rules",
                "All Investments": "/api/investments",
                "Sorted Investments": "/api/investments?sort=true",
                "Valid Investments": "/api/valid_investments",
                "Violating Investments": "/api/violating_investments",
            },
            "status": "API is running",
        })

    return app


def init_db(app):
    """Create tables and load the CSVs if the database is empty."""
    with app.app_context():
        db.create_all()
        if BudgetRule.query.count() == 0:
            load_data(app.config["BUDGET_CSV"], app.config["INVESTMENTS_CSV"])


def _clean(value):
    return value.strip() if isinstance(value, str) and value.strip() else None


def load_data(budget_csv, investments_csv):
    try:
        budget_df = pd.read_csv(budget_csv)
        for _, row in budget_df.iterrows():
            db.session.add(BudgetRule(
                id=int(row["ID"]),
                amount=float(row["Amount"]),
                time_period=_clean(row["Time Period"]) if pd.notna(row["Time Period"]) else None,
                sector=_clean(row["Sector"]) if pd.notna(row["Sector"]) else None,
            ))

        investments_df = pd.read_csv(investments_csv)
        for _, row in investments_df.iterrows():
            db.session.add(Investment(
                id=int(row["ID"]),
                date=datetime.strptime(row["Date"], "%d/%m/%Y"),
                amount=float(row["Amount"]),
                sector=row["Sector"].strip(),
            ))

        db.session.commit()
        print("Data loaded successfully!")
    except Exception as e:
        db.session.rollback()
        print(f"Error loading data: {e}")
        raise
