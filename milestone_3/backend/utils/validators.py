"""
Validation utilities for input validation and data sanitization
"""
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Union

class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass

class Validators:
    """Collection of validation utilities"""
    
    # Regular expressions for common validations
    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    PASSWORD_REGEX = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{8,}$')
    FILENAME_REGEX = re.compile(r'^[a-zA-Z0-9._-]+$')
    
    @staticmethod
    def validate_email(email: str) -> Dict[str, Any]:
        """Validate email format"""
        if not email:
            return {'valid': False, 'error': 'Email is required'}
        
        email = email.strip().lower()
        
        if len(email) > 254:  # RFC 5321 limit
            return {'valid': False, 'error': 'Email is too long'}
        
        if not Validators.EMAIL_REGEX.match(email):
            return {'valid': False, 'error': 'Invalid email format'}
        
        return {'valid': True, 'cleaned_value': email}
    
    @staticmethod
    def validate_password(password: str, min_length: int = 6, require_complexity: bool = False) -> Dict[str, Any]:
        """Validate password strength"""
        if not password:
            return {'valid': False, 'error': 'Password is required'}
        
        if len(password) < min_length:
            return {'valid': False, 'error': f'Password must be at least {min_length} characters long'}
        
        if len(password) > 128:  # Reasonable upper limit
            return {'valid': False, 'error': 'Password is too long'}
        
        if require_complexity:
            if not re.search(r'[a-z]', password):
                return {'valid': False, 'error': 'Password must contain at least one lowercase letter'}
            
            if not re.search(r'[A-Z]', password):
                return {'valid': False, 'error': 'Password must contain at least one uppercase letter'}
            
            if not re.search(r'\d', password):
                return {'valid': False, 'error': 'Password must contain at least one number'}
            
            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                return {'valid': False, 'error': 'Password must contain at least one special character'}
        
        return {'valid': True}
    
    @staticmethod
    def validate_filename(filename: str) -> Dict[str, Any]:
        """Validate filename for security"""
        if not filename:
            return {'valid': False, 'error': 'Filename is required'}
        
        # Remove path components
        filename = filename.split('/')[-1].split('\\')[-1]
        
        if not filename:
            return {'valid': False, 'error': 'Invalid filename'}
        
        if len(filename) > 255:  # File system limit
            return {'valid': False, 'error': 'Filename is too long'}
        
        # Check for dangerous characters
        dangerous_chars = ['<', '>', ':', '"', '|', '?', '*', '\0']
        if any(char in filename for char in dangerous_chars):
            return {'valid': False, 'error': 'Filename contains invalid characters'}
        
        # Check for reserved names (Windows)
        reserved_names = ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 
                         'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 
                         'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9']
        
        name_without_ext = filename.rsplit('.', 1)[0].upper()
        if name_without_ext in reserved_names:
            return {'valid': False, 'error': 'Filename uses reserved name'}
        
        return {'valid': True, 'cleaned_value': filename}
    
    @staticmethod
    def validate_file_size(file_size: int, max_size: int = 16 * 1024 * 1024) -> Dict[str, Any]:
        """Validate file size"""
        if file_size <= 0:
            return {'valid': False, 'error': 'Invalid file size'}
        
        if file_size > max_size:
            max_size_mb = max_size / (1024 * 1024)
            return {'valid': False, 'error': f'File size exceeds maximum allowed size of {max_size_mb:.1f}MB'}
        
        return {'valid': True}
    
    @staticmethod
    def validate_pagination(page: int, per_page: int, max_per_page: int = 100) -> Dict[str, Any]:
        """Validate pagination parameters"""
        if page < 1:
            return {'valid': False, 'error': 'Page number must be positive'}
        
        if per_page < 1:
            return {'valid': False, 'error': 'Items per page must be positive'}
        
        if per_page > max_per_page:
            return {'valid': False, 'error': f'Items per page cannot exceed {max_per_page}'}
        
        return {'valid': True}
    
    @staticmethod
    def validate_search_query(query: str, min_length: int = 2, max_length: int = 100) -> Dict[str, Any]:
        """Validate search query"""
        if not query:
            return {'valid': False, 'error': 'Search query is required'}
        
        query = query.strip()
        
        if len(query) < min_length:
            return {'valid': False, 'error': f'Search query must be at least {min_length} characters'}
        
        if len(query) > max_length:
            return {'valid': False, 'error': f'Search query cannot exceed {max_length} characters'}
        
        # Check for SQL injection patterns (basic)
        suspicious_patterns = ['--', ';', 'union', 'select', 'drop', 'delete', 'insert', 'update']
        query_lower = query.lower()
        
        for pattern in suspicious_patterns:
            if pattern in query_lower:
                return {'valid': False, 'error': 'Search query contains invalid characters'}
        
        return {'valid': True, 'cleaned_value': query}
    
    @staticmethod
    def validate_sort_parameters(sort_by: str, sort_order: str, allowed_fields: List[str]) -> Dict[str, Any]:
        """Validate sorting parameters"""
        if sort_by not in allowed_fields:
            return {'valid': False, 'error': f'Invalid sort field. Allowed fields: {", ".join(allowed_fields)}'}
        
        if sort_order not in ['asc', 'desc']:
            return {'valid': False, 'error': 'Sort order must be "asc" or "desc"'}
        
        return {'valid': True}
    
    @staticmethod
    def validate_json_data(data: Any, required_fields: List[str] = None, optional_fields: List[str] = None) -> Dict[str, Any]:
        """Validate JSON data structure"""
        if not isinstance(data, dict):
            return {'valid': False, 'error': 'Data must be a JSON object'}
        
        if required_fields:
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return {'valid': False, 'error': f'Missing required fields: {", ".join(missing_fields)}'}
        
        if optional_fields is not None:  # If optional_fields is provided, restrict to only allowed fields
            allowed_fields = set(required_fields or []) | set(optional_fields)
            extra_fields = [field for field in data.keys() if field not in allowed_fields]
            if extra_fields:
                return {'valid': False, 'error': f'Unexpected fields: {", ".join(extra_fields)}'}
        
        return {'valid': True}
    
    @staticmethod
    def validate_id_list(id_list: List[Any], max_length: int = 100) -> Dict[str, Any]:
        """Validate list of IDs"""
        if not isinstance(id_list, list):
            return {'valid': False, 'error': 'ID list must be an array'}
        
        if len(id_list) == 0:
            return {'valid': False, 'error': 'ID list cannot be empty'}
        
        if len(id_list) > max_length:
            return {'valid': False, 'error': f'ID list cannot exceed {max_length} items'}
        
        # Validate each ID
        valid_ids = []
        for i, id_value in enumerate(id_list):
            try:
                valid_id = int(id_value)
                if valid_id <= 0:
                    return {'valid': False, 'error': f'Invalid ID at position {i}: must be positive'}
                valid_ids.append(valid_id)
            except (ValueError, TypeError):
                return {'valid': False, 'error': f'Invalid ID at position {i}: must be a number'}
        
        return {'valid': True, 'cleaned_value': valid_ids}
    
    @staticmethod
    def sanitize_text(text: str, max_length: int = None, allow_html: bool = False) -> str:
        """Sanitize text input"""
        if not isinstance(text, str):
            return str(text) if text is not None else ""
        
        # Remove null bytes
        text = text.replace('\0', '')
        
        # Limit length
        if max_length and len(text) > max_length:
            text = text[:max_length]
        
        # Remove HTML if not allowed
        if not allow_html:
            # Simple HTML removal (for more complex needs, use bleach library)
            text = re.sub(r'<[^>]+>', '', text)
        
        return text.strip()
    
    @staticmethod
    def validate_file_extension(filename: str, allowed_extensions: List[str]) -> Dict[str, Any]:
        """Validate file extension"""
        if not filename:
            return {'valid': False, 'error': 'Filename is required'}
        
        if '.' not in filename:
            return {'valid': False, 'error': 'File must have an extension'}
        
        extension = filename.rsplit('.', 1)[1].lower()
        
        if extension not in [ext.lower() for ext in allowed_extensions]:
            return {'valid': False, 'error': f'File type not allowed. Allowed types: {", ".join(allowed_extensions)}'}
        
        return {'valid': True, 'extension': extension}

class FormValidator:
    """Form validation utility class"""
    
    def __init__(self):
        self.errors = {}
        self.validated_data = {}
    
    def add_error(self, field: str, error: str):
        """Add validation error for a field"""
        if field not in self.errors:
            self.errors[field] = []
        self.errors[field].append(error)
    
    def add_validated_data(self, field: str, value: Any):
        """Add validated data for a field"""
        self.validated_data[field] = value
    
    def validate_field(self, field: str, value: Any, validator_func, *args, **kwargs) -> bool:
        """Validate a single field using a validator function"""
        try:
            result = validator_func(value, *args, **kwargs)
            if result['valid']:
                if 'cleaned_value' in result:
                    self.add_validated_data(field, result['cleaned_value'])
                else:
                    self.add_validated_data(field, value)
                return True
            else:
                self.add_error(field, result['error'])
                return False
        except Exception as e:
            self.add_error(field, f'Validation error: {str(e)}')
            return False
    
    def is_valid(self) -> bool:
        """Check if all validations passed"""
        return len(self.errors) == 0
    
    def get_errors(self) -> Dict[str, List[str]]:
        """Get all validation errors"""
        return self.errors
    
    def get_validated_data(self) -> Dict[str, Any]:
        """Get all validated data"""
        return self.validated_data
    
    def get_first_error(self) -> Optional[str]:
        """Get the first validation error message"""
        if not self.errors:
            return None
        
        first_field = next(iter(self.errors))
        return self.errors[first_field][0]