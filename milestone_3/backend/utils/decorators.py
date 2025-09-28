"""
Decorator utilities for route protection, validation, and common operations
"""
from functools import wraps
from flask import request, jsonify, current_app
from flask_login import current_user
from datetime import datetime, timedelta
import time
from typing import Dict, List, Any, Optional, Callable
from utils.validators import Validators, FormValidator
from utils.helpers import ResponseHelper

def login_required_api(f):
    """API version of login_required that returns JSON responses"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify(ResponseHelper.error_response(
                'Authentication required', 401
            )), 401
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Require admin privileges"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify(ResponseHelper.error_response(
                'Authentication required', 401
            )), 401
        
        # Check if user has admin role (you'd implement this based on your user model)
        if not getattr(current_user, 'is_admin', False):
            return jsonify(ResponseHelper.error_response(
                'Admin privileges required', 403
            )), 403
        
        return f(*args, **kwargs)
    return decorated_function

def validate_json(required_fields: List[str] = None, optional_fields: List[str] = None):
    """Validate JSON request data"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify(ResponseHelper.error_response(
                    'Request must be JSON', 400
                )), 400
            
            data = request.get_json()
            if not data:
                return jsonify(ResponseHelper.error_response(
                    'No JSON data provided', 400
                )), 400
            
            validation_result = Validators.validate_json_data(
                data, required_fields, optional_fields
            )
            
            if not validation_result['valid']:
                return jsonify(ResponseHelper.error_response(
                    validation_result['error'], 400
                )), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_form(validation_rules: Dict[str, Callable]):
    """Validate form data using custom validation rules"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            validator = FormValidator()
            
            # Get data from request
            if request.is_json:
                data = request.get_json() or {}
            else:
                data = request.form.to_dict()
            
            # Apply validation rules
            for field, rule in validation_rules.items():
                value = data.get(field)
                validator.validate_field(field, value, rule)
            
            if not validator.is_valid():
                return jsonify(ResponseHelper.error_response(
                    'Validation failed',
                    400,
                    validator.get_errors()
                )), 400
            
            # Add validated data to request context
            request.validated_data = validator.get_validated_data()
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_file_upload(allowed_extensions: List[str] = None, max_size: int = None):
    """Validate file upload"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'file' not in request.files:
                return jsonify(ResponseHelper.error_response(
                    'No file provided', 400
                )), 400
            
            file = request.files['file']
            
            if file.filename == '':
                return jsonify(ResponseHelper.error_response(
                    'No file selected', 400
                )), 400
            
            # Validate filename
            filename_result = Validators.validate_filename(file.filename)
            if not filename_result['valid']:
                return jsonify(ResponseHelper.error_response(
                    filename_result['error'], 400
                )), 400
            
            # Validate extension
            if allowed_extensions:
                ext_result = Validators.validate_file_extension(
                    file.filename, allowed_extensions
                )
                if not ext_result['valid']:
                    return jsonify(ResponseHelper.error_response(
                        ext_result['error'], 400
                    )), 400
            
            # Validate file size
            if max_size:
                file.seek(0, 2)  # Seek to end
                file_size = file.tell()
                file.seek(0)  # Reset position
                
                size_result = Validators.validate_file_size(file_size, max_size)
                if not size_result['valid']:
                    return jsonify(ResponseHelper.error_response(
                        size_result['error'], 400
                    )), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def rate_limit(max_requests: int = 100, window_minutes: int = 60):
    """Simple rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get client identifier (you might want to use IP + user ID)
            client_id = request.remote_addr
            if current_user.is_authenticated:
                client_id = f"{client_id}:{current_user.id}"
            
            # Create cache key
            cache_key = f"rate_limit:{f.__name__}:{client_id}"
            
            # Get current time window
            now = datetime.utcnow()
            window_start = now - timedelta(minutes=window_minutes)
            
            # In a real implementation, you'd use Redis or similar
            # For now, we'll use a simple in-memory approach (not production-ready)
            if not hasattr(current_app, 'rate_limit_cache'):
                current_app.rate_limit_cache = {}
            
            cache = current_app.rate_limit_cache
            
            # Clean old entries
            if cache_key in cache:
                cache[cache_key] = [
                    timestamp for timestamp in cache[cache_key]
                    if timestamp > window_start
                ]
            else:
                cache[cache_key] = []
            
            # Check rate limit
            if len(cache[cache_key]) >= max_requests:
                return jsonify(ResponseHelper.error_response(
                    'Rate limit exceeded', 429
                )), 429
            
            # Add current request
            cache[cache_key].append(now)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def log_api_call(include_params: bool = True, include_response: bool = False):
    """Log API calls for monitoring"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time.time()
            
            # Log request
            log_data = {
                'function': f.__name__,
                'method': request.method,
                'path': request.path,
                'user_id': current_user.id if current_user.is_authenticated else None,
                'ip_address': request.remote_addr,
                'user_agent': request.headers.get('User-Agent'),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            if include_params:
                log_data['params'] = {
                    'args': request.args.to_dict(),
                    'form': request.form.to_dict() if request.form else None,
                    'json': request.get_json() if request.is_json else None
                }
            
            try:
                response = f(*args, **kwargs)
                
                # Calculate execution time
                execution_time = time.time() - start_time
                log_data['execution_time'] = execution_time
                log_data['status'] = 'success'
                
                if include_response and hasattr(response, 'get_json'):
                    try:
                        log_data['response'] = response.get_json()
                    except Exception:
                        log_data['response'] = 'Could not serialize response'
                
                # Log to your preferred logging system
                current_app.logger.info(f"API Call: {log_data}")
                
                return response
                
            except Exception as e:
                execution_time = time.time() - start_time
                log_data['execution_time'] = execution_time
                log_data['status'] = 'error'
                log_data['error'] = str(e)
                
                current_app.logger.error(f"API Call Error: {log_data}")
                raise
        
        return decorated_function
    return decorator

def cache_response(timeout: int = 300):
    """Simple response caching decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"cache:{f.__name__}:{hash(str(args) + str(kwargs))}"
            
            # In a real implementation, you'd use Redis or similar
            if not hasattr(current_app, 'response_cache'):
                current_app.response_cache = {}
            
            cache = current_app.response_cache
            now = datetime.utcnow()
            
            # Check if cached response exists and is still valid
            if cache_key in cache:
                cached_data, cached_time = cache[cache_key]
                if (now - cached_time).total_seconds() < timeout:
                    return cached_data
            
            # Execute function and cache response
            response = f(*args, **kwargs)
            cache[cache_key] = (response, now)
            
            return response
        return decorated_function
    return decorator

def require_permissions(*permissions):
    """Require specific permissions"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify(ResponseHelper.error_response(
                    'Authentication required', 401
                )), 401
            
            # Check permissions (implement based on your permission system)
            user_permissions = getattr(current_user, 'permissions', [])
            
            for permission in permissions:
                if permission not in user_permissions:
                    return jsonify(ResponseHelper.error_response(
                        f'Permission "{permission}" required', 403
                    )), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def handle_exceptions(default_message: str = "An error occurred"):
    """Handle exceptions and return consistent error responses"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except ValueError as e:
                current_app.logger.warning(f"ValueError in {f.__name__}: {str(e)}")
                return jsonify(ResponseHelper.error_response(
                    str(e), 400
                )), 400
            except PermissionError as e:
                current_app.logger.warning(f"PermissionError in {f.__name__}: {str(e)}")
                return jsonify(ResponseHelper.error_response(
                    "Permission denied", 403
                )), 403
            except FileNotFoundError as e:
                current_app.logger.warning(f"FileNotFoundError in {f.__name__}: {str(e)}")
                return jsonify(ResponseHelper.error_response(
                    "Resource not found", 404
                )), 404
            except Exception as e:
                current_app.logger.error(f"Unexpected error in {f.__name__}: {str(e)}")
                return jsonify(ResponseHelper.error_response(
                    default_message, 500
                )), 500
        return decorated_function
    return decorator

def validate_pagination():
    """Validate pagination parameters from query string"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            
            validation_result = Validators.validate_pagination(page, per_page)
            if not validation_result['valid']:
                return jsonify(ResponseHelper.error_response(
                    validation_result['error'], 400
                )), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def cors_headers(origin: str = "*", methods: List[str] = None, headers: List[str] = None):
    """Add CORS headers to response"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            response = f(*args, **kwargs)
            
            # Handle different response types
            if hasattr(response, 'headers'):
                response.headers['Access-Control-Allow-Origin'] = origin
                
                if methods:
                    response.headers['Access-Control-Allow-Methods'] = ', '.join(methods)
                
                if headers:
                    response.headers['Access-Control-Allow-Headers'] = ', '.join(headers)
            
            return response
        return decorated_function
    return decorator