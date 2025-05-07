# backend/routes/accounts_routes.py
from flask import Blueprint, request, jsonify, session
from models import db, Account, AccountType # Import AccountType as well
from functools import wraps # Import wraps

accounts_bp = Blueprint('accounts_bp', __name__)

# Helper to check if user is logged in (optional, if these are admin-only routes)
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'message': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

@accounts_bp.route('', methods=['POST'])
@login_required  # Account creation should be restricted to logged-in users
def create_account():
    data = request.get_json()
    name = data.get('name')
    number = data.get('number')
    account_type_str = data.get('type')

    if not all([name, number, account_type_str]):
        return jsonify({'message': 'Missing data: name, number, and type are required'}), 400

    try:
        account_type = AccountType(account_type_str) # Validate and convert string to Enum
    except ValueError:
        valid_types = [e.value for e in AccountType]
        return jsonify({'message': f'Invalid account type. Must be one of: {valid_types}'}), 400

    if Account.query.filter_by(number=number).first():
        return jsonify({'message': f'Account number {number} already exists'}), 409
    if Account.query.filter_by(name=name).first():
        return jsonify({'message': f'Account name "{name}" already exists'}), 409

    new_account = Account(name=name, number=number, type=account_type)
    db.session.add(new_account)
    db.session.commit()
    return jsonify(new_account.to_dict()), 201

@accounts_bp.route('', methods=['GET'])
@login_required
def get_accounts():
    accounts = Account.query.order_by(Account.number).all()
    return jsonify([account.to_dict() for account in accounts]), 200

@accounts_bp.route('/<int:account_id>', methods=['GET'])
@login_required
def get_account(account_id):
    account = Account.query.get(account_id)
    if not account:
        return jsonify({'message': 'Account not found'}), 404
    return jsonify(account.to_dict()), 200

@accounts_bp.route('/<int:account_id>', methods=['PUT'])
@login_required
def update_account(account_id):
    account = Account.query.get(account_id)
    if not account:
        return jsonify({'message': 'Account not found'}), 404
        
    data = request.get_json()
    name = data.get('name')
    number = data.get('number')
    account_type_str = data.get('type')
    
    # Check for required fields
    if not all([name, number, account_type_str]):
        return jsonify({'message': 'Missing data: name, number, and type are required'}), 400
    
    # Check uniqueness constraints for name and number if they're changing
    if name != account.name and Account.query.filter_by(name=name).first():
        return jsonify({'message': f'Account name "{name}" already exists'}), 409
        
    if number != account.number and Account.query.filter_by(number=number).first():
        return jsonify({'message': f'Account number {number} already exists'}), 409
    
    # Validate account type
    try:
        account_type = AccountType(account_type_str)
    except ValueError:
        valid_types = [e.value for e in AccountType]
        return jsonify({'message': f'Invalid account type. Must be one of: {valid_types}'}), 400
    
    # Update account
    account.name = name
    account.number = number
    account.type = account_type
    
    db.session.commit()
    return jsonify(account.to_dict()), 200

@accounts_bp.route('/<int:account_id>', methods=['DELETE'])
@login_required
def delete_account(account_id):
    account = Account.query.get(account_id)
    if not account:
        return jsonify({'message': 'Account not found'}), 404
        
    # Check if account has transactions
    if account.transactions and len(account.transactions) > 0:
        return jsonify({'message': 'Cannot delete account with transactions'}), 400
        
    db.session.delete(account)
    db.session.commit()
    return jsonify({'message': f'Account {account.name} deleted successfully'}), 200
