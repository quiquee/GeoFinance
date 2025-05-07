# backend/routes/journal_routes.py
from flask import Blueprint, request, jsonify, session
from models import db, JournalEntry, TransactionLine, Account, AccountType
from decimal import Decimal
from sqlalchemy.exc import IntegrityError
from functools import wraps # Import wraps

journal_bp = Blueprint('journal_bp', __name__)

# Helper to check if user is logged in
def login_required(f):
    @wraps(f) # Important for preserving function metadata
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'message': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

@journal_bp.route('/entries', methods=['POST'])
@login_required
def create_journal_entry():
    data = request.get_json()
    user_id = session['user_id']
    description = data.get('description')
    lines_data = data.get('lines') # Expect a list of {account_id, amount, type}

    if not description or not lines_data or not isinstance(lines_data, list) or len(lines_data) < 2:
        return jsonify({'message': 'Description and at least two transaction lines are required'}), 400

    total_debits = Decimal('0.00')
    total_credits = Decimal('0.00')
    transaction_lines = []

    for line_data in lines_data:
        account_id = line_data.get('account_id')
        amount_str = line_data.get('amount')
        line_type = line_data.get('type') # "debit" or "credit"

        if not all([account_id, amount_str, line_type]):
            return jsonify({'message': 'Each line must have account_id, amount, and type'}), 400
        
        try:
            amount = Decimal(amount_str)
            if amount <= 0:
                raise ValueError("Amount must be positive")
        except (ValueError, TypeError):
            return jsonify({'message': f'Invalid amount: {amount_str}'}), 400

        if line_type.lower() not in ['debit', 'credit']:
            return jsonify({'message': f'Invalid line type: {line_type}. Must be "debit" or "credit".'}), 400

        account = Account.query.get(account_id)
        if not account:
            return jsonify({'message': f'Account with id {account_id} not found'}), 404

        transaction_lines.append(TransactionLine(
            account_id=account_id,
            amount=amount,
            type=line_type.lower()
        ))

        if line_type.lower() == 'debit':
            total_debits += amount
        else:
            total_credits += amount

    if total_debits != total_credits:
        return jsonify({
            'message': 'Debits and credits do not balance',
            'total_debits': str(total_debits),
            'total_credits': str(total_credits)
        }), 400

    try:
        new_entry = JournalEntry(user_id=user_id, description=description, lines=transaction_lines)
        db.session.add(new_entry)
        db.session.commit()
        return jsonify(new_entry.to_dict()), 201
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({'message': 'Database integrity error', 'error': str(e)}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500

@journal_bp.route('/entries', methods=['GET'])
@login_required
def get_journal_entries():
    user_id = session['user_id']
    # TODO: Add pagination
    entries = JournalEntry.query.filter_by(user_id=user_id).order_by(JournalEntry.date.desc()).all()
    return jsonify([entry.to_dict() for entry in entries]), 200

@journal_bp.route('/entries/<int:entry_id>', methods=['GET'])
@login_required
def get_journal_entry(entry_id):
    user_id = session['user_id']
    entry = JournalEntry.query.filter_by(id=entry_id, user_id=user_id).first()
    if not entry:
        return jsonify({'message': 'Journal entry not found'}), 404
    return jsonify(entry.to_dict()), 200

@journal_bp.route('/entries/<int:entry_id>', methods=['PUT'])
@login_required
def update_journal_entry(entry_id):
    user_id = session['user_id']
    entry = JournalEntry.query.filter_by(id=entry_id, user_id=user_id).first()
    if not entry:
        return jsonify({'message': 'Journal entry not found'}), 404
        
    data = request.get_json()
    description = data.get('description')
    lines_data = data.get('lines')
    
    if not description or not lines_data or not isinstance(lines_data, list) or len(lines_data) < 2:
        return jsonify({'message': 'Description and at least two transaction lines are required'}), 400
        
    total_debits = Decimal('0.00')
    total_credits = Decimal('0.00')
    new_transaction_lines = []
    
    for line_data in lines_data:
        account_id = line_data.get('account_id')
        amount_str = line_data.get('amount')
        line_type = line_data.get('type')
        
        if not all([account_id, amount_str, line_type]):
            return jsonify({'message': 'Each line must have account_id, amount, and type'}), 400
            
        try:
            amount = Decimal(amount_str)
            if amount <= 0:
                raise ValueError("Amount must be positive")
        except (ValueError, TypeError):
            return jsonify({'message': f'Invalid amount: {amount_str}'}), 400
            
        if line_type.lower() not in ['debit', 'credit']:
            return jsonify({'message': f'Invalid line type: {line_type}. Must be "debit" or "credit".'}), 400
            
        account = Account.query.get(account_id)
        if not account:
            return jsonify({'message': f'Account with id {account_id} not found'}), 404
            
        new_transaction_lines.append(TransactionLine(
            account_id=account_id,
            amount=amount,
            type=line_type.lower()
        ))
        
        if line_type.lower() == 'debit':
            total_debits += amount
        else:
            total_credits += amount
            
    if total_debits != total_credits:
        return jsonify({
            'message': 'Debits and credits do not balance',
            'total_debits': str(total_debits),
            'total_credits': str(total_credits)
        }), 400
        
    try:
        # Delete existing lines and add new ones
        for line in entry.lines:
            db.session.delete(line)
            
        entry.description = description
        entry.lines = new_transaction_lines
        db.session.commit()
        return jsonify(entry.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500

@journal_bp.route('/entries/<int:entry_id>', methods=['DELETE'])
@login_required
def delete_journal_entry(entry_id):
    user_id = session['user_id']
    entry = JournalEntry.query.filter_by(id=entry_id, user_id=user_id).first()
    if not entry:
        return jsonify({'message': 'Journal entry not found'}), 404
        
    try:
        db.session.delete(entry)
        db.session.commit()
        return jsonify({'message': 'Journal entry deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500
