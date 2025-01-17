from api.utils.database import db

class BudgetRule(db.Model):
    __tablename__ = 'budget_rules'
    
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    time_period = db.Column(db.String(10))
    sector = db.Column(db.String(50))
    
    def to_dict(self):
        return {
            'id': self.id,
            'amount': self.amount,
            'time_period': self.time_period,
            'sector': self.sector
        }