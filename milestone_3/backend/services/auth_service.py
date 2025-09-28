"""
Authentication service for user management
"""
from flask_login import login_user, logout_user
from models.user import User
from config.database import db

class AuthService:
    """Service class for authentication operations"""
    
    @staticmethod
    def register_user(email, password):
        """Register a new user"""
        try:
            # Check if user already exists
            if User.query.filter_by(email=email.lower().strip()).first():
                return {'success': False, 'error': 'Email already registered'}
            
            # Create new user
            user = User(email=email, password=password)
            db.session.add(user)
            db.session.commit()
            
            return {
                'success': True, 
                'user': user.to_dict(),
                'message': 'Registration successful'
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': f'Registration failed: {str(e)}'}
    
    @staticmethod
    def login_user_service(email, password, remember=False):
        """Authenticate and login user"""
        try:
            user = User.query.filter_by(email=email.lower().strip()).first()
            
            if not user:
                return {'success': False, 'error': 'Invalid credentials'}
            
            if not user.is_active:
                return {'success': False, 'error': 'Account is deactivated'}
            
            if not user.check_password(password):
                return {'success': False, 'error': 'Invalid credentials'}
            
            # Login user
            login_user(user, remember=remember)
            user.update_last_login()
            
            return {
                'success': True,
                'user': user.to_dict(),
                'message': 'Login successful'
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Login failed: {str(e)}'}
    
    @staticmethod
    def logout_user_service():
        """Logout current user"""
        try:
            logout_user()
            return {'success': True, 'message': 'Logout successful'}
        except Exception as e:
            return {'success': False, 'error': f'Logout failed: {str(e)}'}
    
    @staticmethod
    def get_user_by_id(user_id):
        """Get user by ID"""
        try:
            user = User.query.get(user_id)
            if not user:
                return {'success': False, 'error': 'User not found'}
            
            return {'success': True, 'user': user.to_dict()}
        except Exception as e:
            return {'success': False, 'error': f'Error fetching user: {str(e)}'}
    
    @staticmethod
    def get_user_profile(user_id):
        """Get comprehensive user profile data"""
        try:
            user = User.query.get(user_id)
            if not user:
                return {'success': False, 'error': 'User not found'}
            
            profile_data = {
                'user': user.to_dict(),
                'stats': user.get_profile_stats(),
                'achievements': user.get_achievements()
            }
            
            return {'success': True, 'profile': profile_data}
        except Exception as e:
            return {'success': False, 'error': f'Error fetching profile: {str(e)}'}
    
    @staticmethod
    def update_user_profile(user_id, **kwargs):
        """Update user profile information"""
        try:
            user = User.query.get(user_id)
            if not user:
                return {'success': False, 'error': 'User not found'}
            
            # Update allowed fields
            allowed_fields = ['email']
            for field, value in kwargs.items():
                if field in allowed_fields and hasattr(user, field):
                    setattr(user, field, value)
            
            db.session.commit()
            
            return {
                'success': True,
                'user': user.to_dict(),
                'message': 'Profile updated successfully'
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': f'Profile update failed: {str(e)}'}
    
    @staticmethod
    def change_password(user_id, current_password, new_password):
        """Change user password"""
        try:
            user = User.query.get(user_id)
            if not user:
                return {'success': False, 'error': 'User not found'}
            
            if not user.check_password(current_password):
                return {'success': False, 'error': 'Current password is incorrect'}
            
            user.set_password(new_password)
            db.session.commit()
            
            return {'success': True, 'message': 'Password changed successfully'}
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': f'Password change failed: {str(e)}'}
    
    @staticmethod
    def deactivate_user(user_id):
        """Deactivate user account"""
        try:
            user = User.query.get(user_id)
            if not user:
                return {'success': False, 'error': 'User not found'}
            
            user.is_active = False
            db.session.commit()
            
            return {'success': True, 'message': 'Account deactivated successfully'}
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': f'Account deactivation failed: {str(e)}'}
    
    @staticmethod
    def delete_user(user_id):
        """Permanently delete user account and all associated data"""
        try:
            user = User.query.get(user_id)
            if not user:
                return {'success': False, 'error': 'User not found'}
            
            # This will cascade delete all analyses due to the relationship
            db.session.delete(user)
            db.session.commit()
            
            return {'success': True, 'message': 'Account deleted successfully'}
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': f'Account deletion failed: {str(e)}'}