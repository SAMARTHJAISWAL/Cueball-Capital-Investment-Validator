from flask import Blueprint, jsonify
from api.models.budget import BudgetRule

budget_bp = Blueprint('budget', __name__)

@budget_bp.route('/api/budget_rules', methods=['GET'])
def get_budget_rules():
    rules = BudgetRule.query.all()
    return jsonify([rule.to_dict() for rule in rules])