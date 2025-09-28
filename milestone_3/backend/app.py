"""
Main Flask application with modular architecture
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import sys

# Add the parent directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import configuration and database
from config.config import get_config
from config.database import db, login_manager, init_database

# Import blueprints
from routes.auth_routes import auth_bp
from routes.user_routes import user_bp
from routes.analysis_routes import analysis_bp
from routes.file_routes import file_bp

# Import services for application context
from services.auth_service import AuthService
from services.analysis_service import AnalysisService

def create_app(config_name=None):
    """Application factory pattern"""
    
    # Create Flask app
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    config = get_config(config_name)
    app.config.from_object(config)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    # Initialize CORS
    CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"], 
         supports_credentials=True)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(file_bp)
    
    # Create database tables
    with app.app_context():
        init_database()

    # Global error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 'Endpoint not found',
            'message': 'The requested resource was not found on this server.'
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'success': False,
            'error': 'Method not allowed',
            'message': f'The {request.method} method is not allowed for this endpoint.'
        }), 405
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': 'An unexpected error occurred. Please try again later.'
        }), 500
    
    @app.errorhandler(413)
    def request_entity_too_large(error):
        return jsonify({
            'success': False,
            'error': 'File too large',
            'message': 'The uploaded file exceeds the maximum allowed size.'
        }), 413

    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        try:
            # Check database connection
            db.session.execute('SELECT 1')
            db_status = 'healthy'
        except Exception as e:
            db_status = f'unhealthy: {str(e)}'
        
        return jsonify({
            'success': True,
            'status': 'healthy',
            'database': db_status,
            'version': '1.0.0',
            'environment': config_name
        }), 200
    
    # API info endpoint
    @app.route('/api/info', methods=['GET'])
    def api_info():
        """API information endpoint"""
        return jsonify({
            'success': True,
            'api': {
                'name': 'AI Skill Matcher API',
                'version': '1.0.0',
                'description': 'API for AI-powered skill extraction and job matching',
                'environment': config_name
            },
            'endpoints': {
                'authentication': '/api/auth/*',
                'user_management': '/api/user/*',
                'analysis': '/api/analysis/*',
                'file_processing': '/api/file/*'
            },
            'features': [
                'PDF and text file processing',
                'AI-powered skill extraction',
                'Job matching and analysis',
                'User account management',
                'Analysis history and statistics',
                'Secure file upload and validation'
            ]
        }), 200
    
    # Global statistics endpoint (public)
    @app.route('/api/stats/global', methods=['GET'])
    def global_stats():
        """Get global platform statistics"""
        try:
            result = AnalysisService.get_global_statistics()
            
            if result['success']:
                return jsonify(result), 200
            else:
                return jsonify(result), 500
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Failed to get global statistics: {str(e)}'
            }), 500
    
    # Before request handlers
    @app.before_request
    def before_request():
        """Before request handler"""
        # Add request ID for logging
        request.request_id = os.urandom(16).hex()
        
        # Log request info in debug mode
        if app.debug:
            app.logger.debug(f"Request {request.request_id}: {request.method} {request.path}")
    
    # After request handlers
    @app.after_request
    def after_request(response):
        """After request handler"""
        # Add security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Add request ID to response headers
        if hasattr(request, 'request_id'):
            response.headers['X-Request-ID'] = request.request_id
        
        return response
    
    return app

# Create application instance
app = create_app()

if __name__ == '__main__':
    # Development server
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    print("🚀 Starting AI Skill Matcher API...")
    print(f"📊 Environment: {os.environ.get('FLASK_ENV', 'development')}")
    print(f"🌐 Server: http://localhost:{port}")
    print(f"🔧 Debug mode: {debug}")
    print("📚 API Documentation: http://localhost:5000/api/info")
    print("💚 Health check: http://localhost:5000/health")
    
    app.run(host='0.0.0.0', port=port, debug=debug)