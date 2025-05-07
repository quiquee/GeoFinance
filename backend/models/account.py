# backend/models/account.py
import enum
from .base import db

class AccountType(enum.Enum):
    ASSET = "asset"
    LIABILITY = "liability"
    INCOME = "income"
    EXPENSE = "expense"
    OFF_BALANCE = "offBalance" # Corrected enum member name

class Account(db.Model):
    __tablename__ = 'accounts' # Explicit table name

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True) # Account names should be unique
    number = db.Column(db.String(20), nullable=False, unique=True) # Account numbers should be unique
    type = db.Column(db.Enum(AccountType), nullable=False)

    # Relationship for journal entries (optional, but good for ORM features)
    # transaction_lines = db.relationship('TransactionLine', back_populates='account')

    def __repr__(self):
        return f'<Account {self.number} - {self.name} ({self.type.value})>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'number': self.number,
            'type': self.type.value
        }
