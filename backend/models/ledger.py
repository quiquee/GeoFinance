# backend/models/ledger.py
from .base import db

class Ledger(db.Model):
    __tablename__ = 'ledgers'
    # The ledger is uniquely identified by the user_id
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    # No other fields are needed as per the requirement that it only has a unique number (user_id)

    user = db.relationship('User', backref=db.backref('ledger', uselist=False))

    def __repr__(self):
        return f'<Ledger for User {self.user_id}>'

    def to_dict(self):
        return {
            'user_id': self.user_id
            # Balances will be calculated on demand, not stored directly here
        }
