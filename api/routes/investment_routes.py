from flask import Blueprint, jsonify, request

from api.models.budget import BudgetRule
from api.models.investment import Investment
from api.utils.validators import find_violations

investment_bp = Blueprint("investment", __name__)


def _chronological():
    return Investment.query.order_by(Investment.date, Investment.id).all()


@investment_bp.route("/api/investments", methods=["GET"])
def get_investments():
    """All investments; ?sort=true orders them by date."""
    if request.args.get("sort", "false").lower() == "true":
        investments = _chronological()
    else:
        investments = Investment.query.order_by(Investment.id).all()
    return jsonify([inv.to_dict() for inv in investments])


@investment_bp.route("/api/valid_investments", methods=["GET"])
def get_valid_investments():
    investments = _chronological()
    violating = find_violations(investments, BudgetRule.query.all())
    return jsonify([inv.to_dict() for inv in investments if inv.id not in violating])


@investment_bp.route("/api/violating_investments", methods=["GET"])
def get_violating_investments():
    investments = _chronological()
    violating = find_violations(investments, BudgetRule.query.all())
    return jsonify([inv.to_dict() for inv in investments if inv.id in violating])
