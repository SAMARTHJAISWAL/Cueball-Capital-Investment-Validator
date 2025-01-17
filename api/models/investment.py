from datetime import datetime
from api.utils.database import db

class Investment(db.Model):
    __tablename__ = 'investments'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    sector = db.Column(db.String(50), nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.strftime('%d/%m/%Y'),
            'amount': self.amount,
            'sector': self.sector
        }