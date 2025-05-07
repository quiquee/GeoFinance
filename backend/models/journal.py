# backend/models/journal.py
from .base import db
from sqlalchemy.sql import func # For default timestamp

class JournalEntry(db.Model):
    __tablename__ = 'journal_entries'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.DateTime(timezone=True), server_default=func.now())
    description = db.Column(db.String(255), nullable=False)

    user = db.relationship('User')
    lines = db.relationship('TransactionLine', back_populates='journal_entry', cascade="all, delete-orphan")

    def to_dict(self, include_lines=True):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'date': self.date.isoformat(),
            'description': self.description,
        }
        if include_lines:
            data['lines'] = [line.to_dict() for line in self.lines]
        return data

class TransactionLine(db.Model):
    __tablename__ = 'transaction_lines'
    id = db.Column(db.Integer, primary_key=True)
    journal_entry_id = db.Column(db.Integer, db.ForeignKey('journal_entries.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False) # Precision 10, 2 decimal places
    type = db.Column(db.String(10), nullable=False) # "debit" or "credit"

    journal_entry = db.relationship('JournalEntry', back_populates='lines')
    account = db.relationship('Account') # Removed back_populates='transaction_lines' from here, will add to Account if needed

    def to_dict(self):
        return {
            'id': self.id,
            'journal_entry_id': self.journal_entry_id,
            'account_id': self.account_id,
            'account_name': self.account.name if self.account else None, # Include account name
            'account_number': self.account.number if self.account else None, # Include account number
            'amount': str(self.amount), # Convert Decimal to string for JSON
            'type': self.type
        }
