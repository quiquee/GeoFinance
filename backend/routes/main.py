from flask import Blueprint, request, jsonify, session
from models import db, User
from werkzeug.security import generate_password_hash

main_bp = Blueprint('main', __name__)

@main_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'Username already exists'}), 409

    new_user = User(username=username)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    # Log the user in immediately after registration
    session['user_id'] = new_user.id
    session['username'] = new_user.username

    # Return user info along with success message
    return jsonify({
        'message': 'User registered successfully',
        'user': {'id': new_user.id, 'username': new_user.username}
    }), 201

@main_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        # Password is correct, set session variables
        session['user_id'] = user.id
        session['username'] = user.username
        return jsonify({
            'message': 'Login successful',
            'user': {'id': user.id, 'username': user.username}
        }), 200
    else:
        # Invalid credentials
        return jsonify({'message': 'Invalid username or password'}), 401

@main_bp.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return jsonify({'message': 'Logged out successfully'}), 200

@main_bp.route('/status', methods=['GET'])
def status():
    if 'user_id' in session:
        return jsonify({
            'logged_in': True,
            'user': {'id': session['user_id'], 'username': session['username']}
        }), 200
    else:
        return jsonify({'logged_in': False}), 200
