from flask import Blueprint, jsonify

apitest_bp = Blueprint('apitest', __name__)

# List of endpoints to test, with metadata for the frontend
API_ENDPOINTS = [
    # Authentication endpoints
    {
        'name': 'Register',
        'method': 'POST',
        'path': '/api/register',
        'fields': [
            {'name': 'username', 'type': 'text', 'required': True},
            {'name': 'password', 'type': 'password', 'required': True}
        ]
    },
    {
        'name': 'Login',
        'method': 'POST',
        'path': '/api/login',
        'fields': [
            {'name': 'username', 'type': 'text', 'required': True},
            {'name': 'password', 'type': 'password', 'required': True}
        ]
    },
    {
        'name': 'Logout',
        'method': 'POST',
        'path': '/api/logout',
        'fields': []
    },
    {
        'name': 'Status',
        'method': 'GET',
        'path': '/api/status',
        'fields': []
    },
    
    # Ledger management endpoints
    {
        'name': 'Get User Ledger',
        'method': 'GET',
        'path': '/api/ledger',
        'fields': []
    },
    {
        'name': 'Delete User Ledger',
        'method': 'DELETE',
        'path': '/api/ledger',
        'fields': []
    },
    {
        'name': 'Get Ledger Balance',
        'method': 'GET',
        'path': '/api/ledger/balance',
        'fields': []
    },
    {
        'name': 'Get Trial Balance',
        'method': 'GET',
        'path': '/api/ledger/trial-balance',
        'fields': []
    },
    {
        'name': 'Get Income Statement',
        'method': 'GET',
        'path': '/api/ledger/income-statement',
        'fields': []
    },
    {
        'name': 'Get Balance Sheet',
        'method': 'GET',
        'path': '/api/ledger/balance-sheet',
        'fields': []
    },
    
    # Account management endpoints
    {
        'name': 'Create Account',
        'method': 'POST',
        'path': '/api/ledger/accounts',
        'fields': [
            {'name': 'name', 'type': 'text', 'required': True},
            {'name': 'number', 'type': 'text', 'required': True},
            {'name': 'type', 'type': 'text', 'required': True}
        ]
    },
    {
        'name': 'List All Accounts',
        'method': 'GET',
        'path': '/api/ledger/accounts',
        'fields': []
    },
    {
        'name': 'Get Account by ID',
        'method': 'GET',
        'path': '/api/ledger/accounts/1',
        'fields': []
    },
    {
        'name': 'Update Account',
        'method': 'PUT',
        'path': '/api/ledger/accounts/1',
        'fields': [
            {'name': 'name', 'type': 'text', 'required': True},
            {'name': 'number', 'type': 'text', 'required': True},
            {'name': 'type', 'type': 'text', 'required': True}
        ]
    },
    {
        'name': 'Delete Account',
        'method': 'DELETE',
        'path': '/api/ledger/accounts/1',
        'fields': []
    },
    
    # Journal entry endpoints
    {
        'name': 'Create Journal Entry',
        'method': 'POST',
        'path': '/api/ledger/journal/entries',
        'fields': [
            {'name': 'description', 'type': 'text', 'required': True},
            {'name': 'lines', 'type': 'text', 'required': True}
        ]
    },
    {
        'name': 'List Journal Entries',
        'method': 'GET',
        'path': '/api/ledger/journal/entries',
        'fields': []
    },
    {
        'name': 'Get Journal Entry',
        'method': 'GET',
        'path': '/api/ledger/journal/entries/1',
        'fields': []
    },
    {
        'name': 'Update Journal Entry',
        'method': 'PUT',
        'path': '/api/ledger/journal/entries/1',
        'fields': [
            {'name': 'description', 'type': 'text', 'required': True},
            {'name': 'lines', 'type': 'text', 'required': True}
        ]
    },
    {
        'name': 'Delete Journal Entry',
        'method': 'DELETE',
        'path': '/api/ledger/journal/entries/1',
        'fields': []
    }
]

@apitest_bp.route('/api/apitest/endpoints', methods=['GET'])
def get_apitest_endpoints():
    return jsonify(API_ENDPOINTS)