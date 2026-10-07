from flask import Blueprint, request, jsonify, session
from database.mongodb import get_db

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Default admin and user credentials for college project demonstration
DEMO_USERS = {
    "admin": {"username": "admin", "name": "System Administrator", "role": "admin", "password": "admin123"},
    "user": {"username": "user", "name": "Faculty User", "role": "user", "password": "user123"}
}

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json() or {}
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()

        if not username or not password:
            return jsonify({'success': False, 'message': 'Username and password are required'}), 400

        user = DEMO_USERS.get(username)
        if not user or user['password'] != password:
            return jsonify({'success': False, 'message': 'Invalid username or password'}), 401

        session['user'] = {
            'username': user['username'],
            'name': user['name'],
            'role': user['role']
        }

        return jsonify({
            'success': True,
            'message': f"Welcome back, {user['name']}!",
            'user': session['user']
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f"Login failed: {str(e)}"}), 500

@auth_bp.route('/logout', methods=['POST', 'GET'])
def logout():
    session.pop('user', None)
    return jsonify({'success': True, 'message': 'Logged out successfully'}), 200

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    user = session.get('user')
    if not user:
        # Default guest session for demo if not logged in
        return jsonify({
            'success': True,
            'logged_in': False,
            'user': {'username': 'guest', 'name': 'Guest User', 'role': 'guest'}
        }), 200
        
    return jsonify({
        'success': True,
        'logged_in': True,
        'user': user
    }), 200
