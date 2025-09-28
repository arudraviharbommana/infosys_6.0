"""
Analysis result model for storing skill matching data
"""
import json
from datetime import datetime
from config.database import db

class AnalysisResult(db.Model):
    """Analysis result model for storing skill matching results"""
    
    __tablename__ = 'analysis_result'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    
    # Content storage
    resume_content = db.Column(db.Text, nullable=False)
    job_description = db.Column(db.Text, nullable=False)
    
    # Results
    match_score = db.Column(db.Float, nullable=False)
    detailed_analysis = db.Column(db.Text, nullable=False)  # JSON string
    strength_assessments = db.Column(db.Text)  # JSON string for strength assessments
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Analysis metadata
    resume_file_name = db.Column(db.String(255))
    job_file_name = db.Column(db.String(255))
    processing_time = db.Column(db.Float)  # Time taken to process in seconds
    
    def __init__(self, user_id, resume_content, job_description, match_score, 
                 detailed_analysis, strength_assessments=None, **kwargs):
        """Initialize analysis result"""
        self.user_id = user_id
        self.resume_content = resume_content
        self.job_description = job_description
        self.match_score = match_score
        self.detailed_analysis = json.dumps(detailed_analysis) if isinstance(detailed_analysis, dict) else detailed_analysis
        self.strength_assessments = json.dumps(strength_assessments) if isinstance(strength_assessments, dict) else strength_assessments
        
        # Optional metadata
        self.resume_file_name = kwargs.get('resume_file_name')
        self.job_file_name = kwargs.get('job_file_name')
        self.processing_time = kwargs.get('processing_time')
    
    def get_detailed_analysis(self):
        """Get detailed analysis as dictionary"""
        try:
            return json.loads(self.detailed_analysis) if self.detailed_analysis else {}
        except json.JSONDecodeError:
            return {}
    
    def get_strength_assessments(self):
        """Get strength assessments as dictionary"""
        try:
            return json.loads(self.strength_assessments) if self.strength_assessments else {}
        except json.JSONDecodeError:
            return {}
    
    def get_preview_data(self):
        """Get preview data for listing views"""
        return {
            'id': self.id,
            'match_score': self.match_score,
            'created_at': self.created_at.isoformat(),
            'resume_preview': self.resume_content[:100] + "..." if len(self.resume_content) > 100 else self.resume_content,
            'job_preview': self.job_description[:100] + "..." if len(self.job_description) > 100 else self.job_description,
            'resume_file_name': self.resume_file_name,
            'job_file_name': self.job_file_name
        }
    
    def get_full_data(self):
        """Get complete analysis data"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'match_score': self.match_score,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'resume_content': self.resume_content,
            'job_description': self.job_description,
            'detailed_analysis': self.get_detailed_analysis(),
            'strength_assessments': self.get_strength_assessments(),
            'resume_file_name': self.resume_file_name,
            'job_file_name': self.job_file_name,
            'processing_time': self.processing_time
        }
    
    def get_skills_summary(self):
        """Get summary of skills from detailed analysis"""
        analysis = self.get_detailed_analysis()
        skills_analysis = analysis.get('skills_analysis', {})
        
        return {
            'matched_skills': skills_analysis.get('matched_skills', []),
            'missing_skills': skills_analysis.get('missing_skills', []),
            'extra_skills': skills_analysis.get('extra_skills', []),
            'total_resume_skills': len(skills_analysis.get('resume_skills', [])),
            'total_job_skills': len(skills_analysis.get('job_skills', []))
        }
    
    @staticmethod
    def get_user_statistics(user_id):
        """Get statistics for a specific user"""
        analyses = AnalysisResult.query.filter_by(user_id=user_id).all()
        
        if not analyses:
            return {
                'total_analyses': 0,
                'average_score': 0,
                'best_score': 0,
                'worst_score': 0,
                'score_trend': [],
                'most_common_skills': []
            }
        
        scores = [a.match_score for a in analyses]
        
        # Calculate score trend (last 10 analyses)
        recent_analyses = sorted(analyses, key=lambda x: x.created_at)[-10:]
        score_trend = [(a.created_at.isoformat(), a.match_score) for a in recent_analyses]
        
        # Get most common skills
        all_matched_skills = []
        for analysis in analyses:
            skills = analysis.get_skills_summary()
            all_matched_skills.extend(skills['matched_skills'])
        
        # Count skill frequency
        skill_counts = {}
        for skill in all_matched_skills:
            skill_counts[skill] = skill_counts.get(skill, 0) + 1
        
        most_common_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'total_analyses': len(analyses),
            'average_score': round(sum(scores) / len(scores), 1),
            'best_score': max(scores),
            'worst_score': min(scores),
            'score_trend': score_trend,
            'most_common_skills': most_common_skills
        }
    
    def __repr__(self):
        return f'<AnalysisResult {self.id}: {self.match_score}% match>'