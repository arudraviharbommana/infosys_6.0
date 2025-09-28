"""
User model and authentication functionality
"""
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from config.database import db

class User(UserMixin, db.Model):
    """User model for authentication and profile management"""
    
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relationship to analyses
    analyses = db.relationship('AnalysisResult', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, email, password):
        """Initialize user with email and password"""
        self.email = email.lower().strip()
        self.set_password(password)
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def get_profile_stats(self):
        """Get user profile statistics"""
        from models.analysis import AnalysisResult
        
        analyses = AnalysisResult.query.filter_by(user_id=self.id).all()
        total_analyses = len(analyses)
        
        if total_analyses == 0:
            return {
                'total_analyses': 0,
                'average_score': 0,
                'best_score': 0,
                'last_activity': None
            }
        
        scores = [analysis.match_score for analysis in analyses]
        average_score = sum(scores) / len(scores)
        best_score = max(scores)
        last_activity = max(analysis.created_at for analysis in analyses)
        
        return {
            'total_analyses': total_analyses,
            'average_score': round(average_score, 1),
            'best_score': best_score,
            'last_activity': last_activity.isoformat()
        }
    
    def get_achievements(self):
        """Get user achievements based on activity"""
        stats = self.get_profile_stats()
        total_analyses = stats['total_analyses']
        best_score = stats['best_score']
        
        return {
            'first_match': total_analyses >= 1,
            'analyzer': total_analyses >= 5,
            'high_scorer': best_score >= 80,
            'expert_user': total_analyses >= 10,
            'perfectionist': best_score >= 95,
            'consistent': total_analyses >= 3 and stats['average_score'] >= 70
        }
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'is_active': self.is_active
        }
    
    def __repr__(self):
        return f'<User {self.email}>'