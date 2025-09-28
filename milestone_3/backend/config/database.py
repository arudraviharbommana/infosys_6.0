"""
Database initialization and configuration
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def init_db(app):
    """Initialize database with Flask app"""
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Configure login manager
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from models.user import User
        return User.query.get(int(user_id))
    
    return db

def create_tables(app):
    """Create all database tables"""
    with app.app_context():
        # Import models to ensure they are registered
        from models.user import User
        from models.analysis import AnalysisResult
        
        db.create_all()
        print("Database tables created successfully!")

def init_database():
    """Initialize database tables (alias for create_tables)"""
    # Import models to ensure they are registered
    from models.user import User
    from models.analysis import AnalysisResult
    
    db.create_all()
    print("Database initialized successfully!")