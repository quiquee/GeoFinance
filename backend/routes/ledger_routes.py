# backend/routes/ledger_routes.py
from flask import Blueprint, jsonify, session, request
from models import db, Ledger, Account, AccountType, TransactionLine, JournalEntry
from sqlalchemy import func, case
from decimal import Decimal
from functools import wraps

ledger_bp = Blueprint('ledger_bp', __name__)

# Helper to check if user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'message': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

# Main ledger management endpoints

@ledger_bp.route('', methods=['GET'])
@login_required
def get_user_ledger():
    """Get ledger for current user or create a new one if it doesn't exist."""
    user_id = session['user_id']
    ledger = Ledger.query.get(user_id)
    
    # Create ledger if it doesn't exist
    if not ledger:
        new_ledger = Ledger(user_id=user_id)
        db.session.add(new_ledger)
        db.session.commit()
        ledger = new_ledger
        
    return jsonify({
        'user_id': ledger.user_id, 
        'message': 'Ledger active'
    }), 200

@ledger_bp.route('', methods=['DELETE'])
@login_required
def delete_user_ledger():
    """Delete a user's ledger and all related data. Use with caution."""
    user_id = session['user_id']
    
    # Check if ledger exists
    ledger = Ledger.query.get(user_id)
    if not ledger:
        return jsonify({'message': 'Ledger not found'}), 404
    
    # Check for journal entries
    entries = JournalEntry.query.filter_by(user_id=user_id).count()
    if entries > 0:
        return jsonify({
            'message': f'Cannot delete ledger with {entries} journal entries. Delete all entries first.',
            'entries_count': entries
        }), 400
    
    try:
        db.session.delete(ledger)
        db.session.commit()
        return jsonify({'message': 'Ledger deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500

# Reporting endpoints

@ledger_bp.route('/balance', methods=['GET'])
@login_required
def get_ledger_balance():
    """Get account balances for the current user's ledger."""
    user_id = session['user_id']

    # Calculate sum of debits and credits for each account for the user
    balances_query = db.session.query(
        Account.id.label('account_id'),
        Account.name.label('account_name'),
        Account.number.label('account_number'),
        Account.type.label('account_type'),
        func.sum(
            case(
                (TransactionLine.type == 'debit', TransactionLine.amount),
                (TransactionLine.type == 'credit', -TransactionLine.amount),
                else_=0
            )
        ).label('balance_change')
    ).join(TransactionLine.account)\
    .join(TransactionLine.journal_entry)\
    .filter(JournalEntry.user_id == user_id)\
    .group_by(Account.id, Account.name, Account.number, Account.type)\
    .all()

    # Get all accounts to include those with no transactions (balance 0)
    all_accounts = Account.query.order_by(Account.number).all()
    balances_map = {b.account_id: b.balance_change for b in balances_query}

    ledger_report = []
    for acc in all_accounts:
        balance_change = balances_map.get(acc.id, Decimal('0.00'))
        current_balance = Decimal('0.00')

        if acc.type in [AccountType.ASSET, AccountType.EXPENSE]:
            # For ASSET and EXPENSE accounts, debit increases balance
            current_balance = balance_change
        elif acc.type in [AccountType.LIABILITY, AccountType.INCOME, AccountType.OFF_BALANCE]:
            # For LIABILITY, INCOME, and OFF_BALANCE accounts, credit increases balance
            current_balance = -balance_change
        
        ledger_report.append({
            'account_id': acc.id,
            'account_name': acc.name,
            'account_number': acc.number,
            'account_type': acc.type.value,
            'balance': str(current_balance)
        })

    return jsonify(ledger_report), 200

@ledger_bp.route('/trial-balance', methods=['GET'])
@login_required
def get_trial_balance():
    """Get trial balance report showing debit and credit balances of all accounts."""
    user_id = session['user_id']
    
    # Calculate sum of debits and credits for each account
    trial_balance_query = db.session.query(
        Account.id.label('account_id'),
        Account.name.label('account_name'),
        Account.number.label('account_number'),
        Account.type.label('account_type'),
        func.sum(case((TransactionLine.type == 'debit', TransactionLine.amount), else_=0)).label('debit_total'),
        func.sum(case((TransactionLine.type == 'credit', TransactionLine.amount), else_=0)).label('credit_total')
    ).join(TransactionLine.account)\
    .join(TransactionLine.journal_entry)\
    .filter(JournalEntry.user_id == user_id)\
    .group_by(Account.id, Account.name, Account.number, Account.type)\
    .all()
    
    # Prepare trial balance report
    trial_balance = []
    total_debits = Decimal('0.00')
    total_credits = Decimal('0.00')
    
    for acc in trial_balance_query:
        debit_balance = Decimal(str(acc.debit_total)) if acc.debit_total else Decimal('0.00')
        credit_balance = Decimal(str(acc.credit_total)) if acc.credit_total else Decimal('0.00')
        
        total_debits += debit_balance
        total_credits += credit_balance
        
        trial_balance.append({
            'account_id': acc.account_id,
            'account_name': acc.account_name,
            'account_number': acc.account_number,
            'account_type': acc.account_type.value,
            'debit_balance': str(debit_balance),
            'credit_balance': str(credit_balance)
        })
    
    return jsonify({
        'trial_balance': trial_balance,
        'total_debits': str(total_debits),
        'total_credits': str(total_credits),
        'balanced': total_debits == total_credits
    }), 200

@ledger_bp.route('/income-statement', methods=['GET'])
@login_required
def get_income_statement():
    """Get income statement showing revenues, expenses, and net income."""
    user_id = session['user_id']
    
    # Calculate balance for income and expense accounts
    income_statement_query = db.session.query(
        Account.id.label('account_id'),
        Account.name.label('account_name'),
        Account.number.label('account_number'),
        Account.type.label('account_type'),
        func.sum(
            case(
                (TransactionLine.type == 'debit', TransactionLine.amount),
                (TransactionLine.type == 'credit', -TransactionLine.amount),
                else_=0
            )
        ).label('balance_change')
    ).join(TransactionLine.account)\
    .join(TransactionLine.journal_entry)\
    .filter(JournalEntry.user_id == user_id)\
    .filter(Account.type.in_([AccountType.INCOME, AccountType.EXPENSE]))\
    .group_by(Account.id, Account.name, Account.number, Account.type)\
    .all()
    
    income_accounts = []
    expense_accounts = []
    total_income = Decimal('0.00')
    total_expenses = Decimal('0.00')
    
    for acc in income_statement_query:
        balance_change = acc.balance_change or Decimal('0.00')
        
        if acc.account_type == AccountType.INCOME:
            # For income accounts, credit increases balance (negative balance_change means positive income)
            account_balance = -balance_change
            total_income += account_balance
            
            income_accounts.append({
                'account_id': acc.account_id,
                'account_name': acc.account_name,
                'account_number': acc.account_number,
                'balance': str(account_balance)
            })
        elif acc.account_type == AccountType.EXPENSE:
            # For expense accounts, debit increases balance
            account_balance = balance_change
            total_expenses += account_balance
            
            expense_accounts.append({
                'account_id': acc.account_id,
                'account_name': acc.account_name,
                'account_number': acc.account_number,
                'balance': str(account_balance)
            })
    
    net_income = total_income - total_expenses
    
    return jsonify({
        'income_accounts': income_accounts,
        'expense_accounts': expense_accounts,
        'total_income': str(total_income),
        'total_expenses': str(total_expenses),
        'net_income': str(net_income)
    }), 200

@ledger_bp.route('/balance-sheet', methods=['GET'])
@login_required
def get_balance_sheet():
    """Get balance sheet showing assets, liabilities, and equity."""
    user_id = session['user_id']
    
    # Calculate balance for balance sheet accounts
    balance_sheet_query = db.session.query(
        Account.id.label('account_id'),
        Account.name.label('account_name'),
        Account.number.label('account_number'),
        Account.type.label('account_type'),
        func.sum(
            case(
                (TransactionLine.type == 'debit', TransactionLine.amount),
                (TransactionLine.type == 'credit', -TransactionLine.amount),
                else_=0
            )
        ).label('balance_change')
    ).join(TransactionLine.account)\
    .join(TransactionLine.journal_entry)\
    .filter(JournalEntry.user_id == user_id)\
    .filter(Account.type.in_([AccountType.ASSET, AccountType.LIABILITY, AccountType.OFF_BALANCE]))\
    .group_by(Account.id, Account.name, Account.number, Account.type)\
    .all()
    
    # Get net income for equity
    income_statement = get_income_statement()[0].json
    
    asset_accounts = []
    liability_accounts = []
    equity_accounts = []
    total_assets = Decimal('0.00')
    total_liabilities = Decimal('0.00')
    total_equity = Decimal(income_statement['net_income'])  # Start with net income
    
    for acc in balance_sheet_query:
        balance_change = acc.balance_change or Decimal('0.00')
        
        if acc.account_type == AccountType.ASSET:
            # For asset accounts, debit increases balance
            account_balance = balance_change
            total_assets += account_balance
            
            asset_accounts.append({
                'account_id': acc.account_id,
                'account_name': acc.account_name,
                'account_number': acc.account_number,
                'balance': str(account_balance)
            })
        elif acc.account_type == AccountType.LIABILITY:
            # For liability accounts, credit increases balance
            account_balance = -balance_change
            total_liabilities += account_balance
            
            liability_accounts.append({
                'account_id': acc.account_id,
                'account_name': acc.account_name,
                'account_number': acc.account_number,
                'balance': str(account_balance)
            })
        elif acc.account_type == AccountType.OFF_BALANCE:
            # For equity/off-balance accounts, credit increases balance
            account_balance = -balance_change
            total_equity += account_balance
            
            equity_accounts.append({
                'account_id': acc.account_id,
                'account_name': acc.account_name,
                'account_number': acc.account_number,
                'balance': str(account_balance)
            })
    
    # Add "Retained Earnings" from net income
    equity_accounts.append({
        'account_id': None,
        'account_name': 'Retained Earnings',
        'account_number': None,
        'balance': income_statement['net_income']
    })
    
    return jsonify({
        'asset_accounts': asset_accounts,
        'liability_accounts': liability_accounts,
        'equity_accounts': equity_accounts,
        'total_assets': str(total_assets),
        'total_liabilities': str(total_liabilities),
        'total_equity': str(total_equity),
        'balanced': total_assets == (total_liabilities + total_equity)
    }), 200
