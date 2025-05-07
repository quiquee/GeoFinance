from flask import Blueprint, request, jsonify, session
from werkzeug.security import check_password_hash, generate_password_hash
import os
from models.user import User
from models.base import db

auth_bp = Blueprint('auth', __name__, url_prefix='/api')

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Missing username or password'}), 400
    
    username = data.get('username')
    password = data.get('password')
    
    # Find user by username
    user = User.query.filter_by(username=username).first()
    
    # Check if user exists and password is correct
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'message': 'Invalid username or password'}), 401
    
    # Store user info in session
    session['user_id'] = user.id
    session['username'] = user.username
    
    # Return user info
    return jsonify({
        'user': {
            'id': user.id,
            'username': user.username,
            'name': user.username,  # Use username as name since name field doesn't exist
            'role': getattr(user, 'role', 'user')  # Safely access role field or default to 'user'
        }
    })

@auth_bp.route('/logout', methods=['POST'])
def logout():
    # Clear the session
    session.clear()
    return jsonify({'message': 'Logout successful'})