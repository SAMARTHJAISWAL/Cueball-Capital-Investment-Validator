from flask import Flask, render_template, jsonify
from api.utils.database import db
from api.routes.budget_routes import budget_bp
from api.routes.investment_routes import investment_bp
from config.config import Config
import pandas as pd
from datetime import datetime
from api.models.budget import BudgetRule
from api.models.investment import Investment

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    
    app.register_blueprint(budget_bp)
    app.register_blueprint(investment_bp)
    
    @app.route('/')
    def home():
        return jsonify({
            "message": "Welcome to Cueball Capital Investment API",
            "endpoints": {
                "Budget Rules": "/api/budget_rules",
                "All Investments": "/api/investments",
                "Sorted Investments": "/api/investments?sort=true",
                "Valid Investments": "/api/valid_investments",
                "Violating Investments": "/api/violating_investments"
            },
            "status": "API is running"
        })
    
    return app

def init_db(app):
    with app.app_context():
        db.create_all()
        
        if len(BudgetRule.query.all()) == 0: 
            load_data()

def load_data():
    try:
        budget_df = pd.read_csv('data/budget.csv')
        for _, row in budget_df.iterrows():
            rule = BudgetRule(
                id=row['ID'],
                amount=row['Amount'],
                time_period=row['Time Period'],
                sector=row['Sector'] if pd.notna(row['Sector']) else None
            )
            db.session.add(rule)
        
        investments_df = pd.read_csv('data/investments.csv')
        for _, row in investments_df.iterrows():
            date = datetime.strptime(row['Date'], '%d/%m/%Y')
            investment = Investment(
                id=row['ID'],
                date=date,
                amount=row['Amount'],
                sector=row['Sector']
            )
            db.session.add(investment)
        
        db.session.commit()
        print("Data loaded successfully!")
    except Exception as e:
        db.session.rollback()
        print(f"Error loading data: {str(e)}")
        raise