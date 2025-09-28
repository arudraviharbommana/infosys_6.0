"""
Helper utilities for common operations
"""
import os
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
import json
import re

class DateHelper:
    """Date and time utility functions"""
    
    @staticmethod
    def format_datetime(dt: datetime, format_type: str = 'iso') -> str:
        """Format datetime to string"""
        if not isinstance(dt, datetime):
            return str(dt)
        
        if format_type == 'iso':
            return dt.isoformat()
        elif format_type == 'readable':
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        elif format_type == 'date_only':
            return dt.strftime('%Y-%m-%d')
        elif format_type == 'time_only':
            return dt.strftime('%H:%M:%S')
        else:
            return dt.strftime(format_type)
    
    @staticmethod
    def parse_datetime(date_string: str) -> Optional[datetime]:
        """Parse datetime from string"""
        try:
            # Try ISO format first
            return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        except ValueError:
            try:
                # Try common formats
                formats = [
                    '%Y-%m-%d %H:%M:%S',
                    '%Y-%m-%d',
                    '%d/%m/%Y %H:%M:%S',
                    '%d/%m/%Y',
                    '%m/%d/%Y %H:%M:%S',
                    '%m/%d/%Y'
                ]
                
                for fmt in formats:
                    try:
                        return datetime.strptime(date_string, fmt)
                    except ValueError:
                        continue
                
                return None
            except Exception:
                return None
    
    @staticmethod
    def get_time_ago(dt: datetime) -> str:
        """Get human-readable time ago string"""
        if not isinstance(dt, datetime):
            return "Unknown"
        
        now = datetime.utcnow()
        if dt.tzinfo is not None:
            now = now.replace(tzinfo=dt.tzinfo)
        
        diff = now - dt
        
        if diff.days >= 365:
            years = diff.days // 365
            return f"{years} year{'s' if years != 1 else ''} ago"
        elif diff.days >= 30:
            months = diff.days // 30
            return f"{months} month{'s' if months != 1 else ''} ago"
        elif diff.days >= 1:
            return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
        elif diff.seconds >= 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff.seconds >= 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        else:
            return "Just now"
    
    @staticmethod
    def get_date_range(start_date: datetime, end_date: datetime) -> List[datetime]:
        """Get list of dates in range"""
        dates = []
        current = start_date
        
        while current <= end_date:
            dates.append(current)
            current += timedelta(days=1)
        
        return dates

class FileHelper:
    """File and path utility functions"""
    
    @staticmethod
    def get_file_size_string(size_bytes: int) -> str:
        """Convert file size to human-readable string"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    @staticmethod
    def generate_safe_filename(filename: str) -> str:
        """Generate safe filename by removing/replacing dangerous characters"""
        # Remove path components
        filename = os.path.basename(filename)
        
        # Replace dangerous characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # Remove control characters
        filename = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', filename)
        
        # Limit length
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            max_name_length = 255 - len(ext)
            filename = name[:max_name_length] + ext
        
        # Ensure not empty
        if not filename or filename.startswith('.'):
            filename = f"file_{secrets.token_hex(4)}" + (os.path.splitext(filename)[1] if '.' in filename else '')
        
        return filename
    
    @staticmethod
    def get_file_extension(filename: str) -> str:
        """Get file extension in lowercase"""
        if not filename or '.' not in filename:
            return ''
        return filename.rsplit('.', 1)[1].lower()
    
    @staticmethod
    def is_safe_path(path: str, base_path: str) -> bool:
        """Check if path is safe (within base directory)"""
        try:
            abs_base = os.path.abspath(base_path)
            abs_path = os.path.abspath(os.path.join(base_path, path))
            return abs_path.startswith(abs_base)
        except Exception:
            return False

class TextHelper:
    """Text processing utility functions"""
    
    @staticmethod
    def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
        """Truncate text to maximum length"""
        if len(text) <= max_length:
            return text
        
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
        """Extract keywords from text (simple implementation)"""
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'
        }
        
        # Extract words
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        
        # Filter stop words and short words
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Count frequency
        word_freq = {}
        for word in keywords:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and return top keywords
        sorted_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_keywords[:max_keywords]]
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean text by removing extra whitespace and special characters"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove control characters
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]', '', text)
        
        return text.strip()
    
    @staticmethod
    def generate_slug(text: str, max_length: int = 50) -> str:
        """Generate URL-friendly slug from text"""
        # Convert to lowercase
        slug = text.lower()
        
        # Replace spaces and special characters with hyphens
        slug = re.sub(r'[^a-z0-9]+', '-', slug)
        
        # Remove leading/trailing hyphens
        slug = slug.strip('-')
        
        # Truncate if too long
        if len(slug) > max_length:
            slug = slug[:max_length].rstrip('-')
        
        return slug

class HashHelper:
    """Hashing utility functions"""
    
    @staticmethod
    def generate_hash(data: str, algorithm: str = 'sha256') -> str:
        """Generate hash of data"""
        if algorithm == 'md5':
            return hashlib.md5(data.encode()).hexdigest()
        elif algorithm == 'sha1':
            return hashlib.sha1(data.encode()).hexdigest()
        elif algorithm == 'sha256':
            return hashlib.sha256(data.encode()).hexdigest()
        elif algorithm == 'sha512':
            return hashlib.sha512(data.encode()).hexdigest()
        else:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}")
    
    @staticmethod
    def generate_token(length: int = 32) -> str:
        """Generate random token"""
        return secrets.token_hex(length)
    
    @staticmethod
    def generate_id() -> str:
        """Generate unique ID"""
        return secrets.token_hex(16)

class JSONHelper:
    """JSON utility functions"""
    
    @staticmethod
    def safe_json_loads(json_string: str, default: Any = None) -> Any:
        """Safely load JSON with fallback"""
        try:
            return json.loads(json_string)
        except (json.JSONDecodeError, TypeError):
            return default
    
    @staticmethod
    def safe_json_dumps(data: Any, default: Any = None) -> str:
        """Safely dump JSON with fallback"""
        try:
            return json.dumps(data, default=str, ensure_ascii=False, indent=None, separators=(',', ':'))
        except (TypeError, ValueError):
            return json.dumps(default if default is not None else {})
    
    @staticmethod
    def flatten_dict(data: Dict[str, Any], parent_key: str = '', separator: str = '.') -> Dict[str, Any]:
        """Flatten nested dictionary"""
        items = []
        
        for key, value in data.items():
            new_key = f"{parent_key}{separator}{key}" if parent_key else key
            
            if isinstance(value, dict):
                items.extend(JSONHelper.flatten_dict(value, new_key, separator).items())
            else:
                items.append((new_key, value))
        
        return dict(items)
    
    @staticmethod
    def deep_merge(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries"""
        result = dict1.copy()
        
        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = JSONHelper.deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result

class URLHelper:
    """URL utility functions"""
    
    @staticmethod
    def build_query_string(params: Dict[str, Any]) -> str:
        """Build URL query string from parameters"""
        query_parts = []
        
        for key, value in params.items():
            if value is not None:
                if isinstance(value, (list, tuple)):
                    for item in value:
                        query_parts.append(f"{key}={item}")
                else:
                    query_parts.append(f"{key}={value}")
        
        return "&".join(query_parts)
    
    @staticmethod
    def parse_query_string(query_string: str) -> Dict[str, str]:
        """Parse URL query string to dictionary"""
        params = {}
        
        if not query_string:
            return params
        
        # Remove leading '?' if present
        if query_string.startswith('?'):
            query_string = query_string[1:]
        
        for pair in query_string.split('&'):
            if '=' in pair:
                key, value = pair.split('=', 1)
                params[key] = value
            else:
                params[pair] = ''
        
        return params

class ResponseHelper:
    """API response utility functions"""
    
    @staticmethod
    def success_response(data: Any = None, message: str = None, status_code: int = 200) -> Dict[str, Any]:
        """Create standardized success response"""
        response = {'success': True}
        
        if data is not None:
            response['data'] = data
        
        if message:
            response['message'] = message
        
        return response
    
    @staticmethod
    def error_response(error: str, status_code: int = 400, details: Any = None) -> Dict[str, Any]:
        """Create standardized error response"""
        response = {
            'success': False,
            'error': error
        }
        
        if details is not None:
            response['details'] = details
        
        return response
    
    @staticmethod
    def paginated_response(items: List[Any], pagination: Dict[str, Any], message: str = None) -> Dict[str, Any]:
        """Create standardized paginated response"""
        response = {
            'success': True,
            'data': items,
            'pagination': pagination
        }
        
        if message:
            response['message'] = message
        
        return response