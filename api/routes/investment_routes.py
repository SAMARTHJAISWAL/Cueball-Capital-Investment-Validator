from flask import Blueprint, jsonify, request
from api.models.investment import Investment
from api.utils.validators import check_budget_violation
from sqlalchemy import asc

investment_bp = Blueprint('investment', __name__)

@investment_bp.route('/api/investments', methods=['GET'])
def get_investments():
    sort_by_date = request.args.get('sort', 'false').lower() == 'true'
    
    query = Investment.query
    if sort_by_date:
        query = query.order_by(asc(Investment.date))
    
    investments = query.all()
    return jsonify([inv.to_dict() for inv in investments])

@investment_bp.route('/api/valid_investments', methods=['GET'])
def get_valid_investments():
    investments = Investment.query.all()
    valid_investments = [
        inv for inv in investments 
        if not check_budget_violation(inv)
    ]
    return jsonify([inv.to_dict() for inv in valid_investments])

@investment_bp.route('/api/violating_investments', methods=['GET'])
def get_violating_investments():
    investments = Investment.query.all()
    violating_investments = [
        inv for inv in investments 
        if check_budget_violation(inv)
    ]
    return jsonify([inv.to_dict() for inv in violating_investments])