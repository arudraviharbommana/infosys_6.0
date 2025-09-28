"""
Authentication routes for user registration, login, logout
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        # Validation
        if not email:
            return jsonify({'success': False, 'error': 'Email is required'}), 400
        
        if not password:
            return jsonify({'success': False, 'error': 'Password is required'}), 400
        
        if len(password) < 6:
            return jsonify({'success': False, 'error': 'Password must be at least 6 characters'}), 400
        
        # Validate email format
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return jsonify({'success': False, 'error': 'Invalid email format'}), 400
        
        # Register user
        result = AuthService.register_user(email, password)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Registration failed: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        email = data.get('email', '').strip()
        password = data.get('password', '')
        remember = data.get('remember', False)
        
        # Validation
        if not email:
            return jsonify({'success': False, 'error': 'Email is required'}), 400
        
        if not password:
            return jsonify({'success': False, 'error': 'Password is required'}), 400
        
        # Login user
        result = AuthService.login_user_service(email, password, remember)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 401
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Login failed: {str(e)}'}), 500

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """Logout user"""
    try:
        result = AuthService.logout_user_service()
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Logout failed: {str(e)}'}), 500

@auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    """Get current user information"""
    try:
        result = AuthService.get_user_profile(current_user.id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to get user info: {str(e)}'}), 500

@auth_bp.route('/profile', methods=['PUT'])
@login_required
def update_profile():
    """Update user profile"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Only allow updating certain fields
        allowed_fields = ['email']
        update_data = {k: v for k, v in data.items() if k in allowed_fields}
        
        if not update_data:
            return jsonify({'success': False, 'error': 'No valid fields to update'}), 400
        
        # Validate email if provided
        if 'email' in update_data:
            email = update_data['email'].strip()
            if not email:
                return jsonify({'success': False, 'error': 'Email cannot be empty'}), 400
            
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                return jsonify({'success': False, 'error': 'Invalid email format'}), 400
            
            update_data['email'] = email
        
        result = AuthService.update_user_profile(current_user.id, **update_data)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Profile update failed: {str(e)}'}), 500

@auth_bp.route('/change-password', methods=['PUT'])
@login_required
def change_password():
    """Change user password"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
        confirm_password = data.get('confirm_password', '')
        
        # Validation
        if not current_password:
            return jsonify({'success': False, 'error': 'Current password is required'}), 400
        
        if not new_password:
            return jsonify({'success': False, 'error': 'New password is required'}), 400
        
        if len(new_password) < 6:
            return jsonify({'success': False, 'error': 'New password must be at least 6 characters'}), 400
        
        if new_password != confirm_password:
            return jsonify({'success': False, 'error': 'New passwords do not match'}), 400
        
        if current_password == new_password:
            return jsonify({'success': False, 'error': 'New password must be different from current password'}), 400
        
        result = AuthService.change_password(current_user.id, current_password, new_password)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Password change failed: {str(e)}'}), 500

@auth_bp.route('/deactivate', methods=['PUT'])
@login_required
def deactivate_account():
    """Deactivate user account"""
    try:
        data = request.get_json()
        password = data.get('password', '') if data else ''
        
        if not password:
            return jsonify({'success': False, 'error': 'Password confirmation required'}), 400
        
        # Verify password before deactivation
        if not current_user.check_password(password):
            return jsonify({'success': False, 'error': 'Invalid password'}), 401
        
        result = AuthService.deactivate_user(current_user.id)
        
        if result['success']:
            # Logout user after deactivation
            AuthService.logout_user_service()
            return jsonify(result), 200
        else:
            return jsonify(result), 400
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Account deactivation failed: {str(e)}'}), 500

@auth_bp.route('/delete', methods=['DELETE'])
@login_required
def delete_account():
    """Permanently delete user account"""
    try:
        data = request.get_json()
        password = data.get('password', '') if data else ''
        confirm_deletion = data.get('confirm_deletion', False) if data else False
        
        if not password:
            return jsonify({'success': False, 'error': 'Password confirmation required'}), 400
        
        if not confirm_deletion:
            return jsonify({'success': False, 'error': 'Deletion confirmation required'}), 400
        
        # Verify password before deletion
        if not current_user.check_password(password):
            return jsonify({'success': False, 'error': 'Invalid password'}), 401
        
        user_id = current_user.id
        result = AuthService.delete_user(user_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Account deletion failed: {str(e)}'}), 500

@auth_bp.route('/check-auth', methods=['GET'])
def check_auth():
    """Check if user is authenticated"""
    try:
        if current_user.is_authenticated:
            return jsonify({
                'success': True,
                'authenticated': True,
                'user': current_user.to_dict()
            }), 200
        else:
            return jsonify({
                'success': True,
                'authenticated': False,
                'user': None
            }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': f'Auth check failed: {str(e)}'}), 500