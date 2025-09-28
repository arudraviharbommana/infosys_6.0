"""
Analysis service for managing skill analysis results and statistics
"""
from datetime import datetime, timedelta
from models.analysis import AnalysisResult
from models.user import User
from config.database import db
from sqlalchemy import func, desc

class AnalysisService:
    """Service class for analysis operations"""
    
    @staticmethod
    def save_analysis_result(user_id, analysis_data, filename=None, file_type=None):
        """Save analysis result to database"""
        try:
            analysis = AnalysisResult(
                user_id=user_id,
                filename=filename,
                file_type=file_type,
                analysis_data=analysis_data
            )
            
            db.session.add(analysis)
            db.session.commit()
            
            return {
                'success': True,
                'analysis': analysis.to_dict(),
                'message': 'Analysis saved successfully'
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': f'Failed to save analysis: {str(e)}'
            }
    
    @staticmethod
    def get_user_analyses(user_id, page=1, per_page=10, search=None, sort_by='created_at', sort_order='desc'):
        """Get paginated analyses for a user with search and sorting"""
        try:
            query = AnalysisResult.query.filter_by(user_id=user_id)
            
            # Apply search filter
            if search:
                search_term = f"%{search}%"
                query = query.filter(
                    db.or_(
                        AnalysisResult.filename.ilike(search_term),
                        AnalysisResult.file_type.ilike(search_term)
                    )
                )
            
            # Apply sorting
            if sort_by == 'filename':
                sort_column = AnalysisResult.filename
            elif sort_by == 'file_type':
                sort_column = AnalysisResult.file_type
            else:  # default to created_at
                sort_column = AnalysisResult.created_at
            
            if sort_order == 'desc':
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(sort_column)
            
            # Paginate
            pagination = query.paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
            
            analyses = [analysis.to_dict() for analysis in pagination.items]
            
            return {
                'success': True,
                'analyses': analyses,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'has_prev': pagination.has_prev,
                    'has_next': pagination.has_next,
                    'prev_num': pagination.prev_num,
                    'next_num': pagination.next_num
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to fetch analyses: {str(e)}'
            }
    
    @staticmethod
    def get_analysis_by_id(analysis_id, user_id=None):
        """Get specific analysis by ID"""
        try:
            query = AnalysisResult.query.filter_by(id=analysis_id)
            
            # If user_id provided, ensure analysis belongs to user
            if user_id:
                query = query.filter_by(user_id=user_id)
            
            analysis = query.first()
            
            if not analysis:
                return {
                    'success': False,
                    'error': 'Analysis not found or access denied'
                }
            
            return {
                'success': True,
                'analysis': analysis.to_dict()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to fetch analysis: {str(e)}'
            }
    
    @staticmethod
    def delete_analysis(analysis_id, user_id):
        """Delete analysis by ID (only if owned by user)"""
        try:
            analysis = AnalysisResult.query.filter_by(
                id=analysis_id,
                user_id=user_id
            ).first()
            
            if not analysis:
                return {
                    'success': False,
                    'error': 'Analysis not found or access denied'
                }
            
            db.session.delete(analysis)
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Analysis deleted successfully'
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': f'Failed to delete analysis: {str(e)}'
            }
    
    @staticmethod
    def get_user_analysis_statistics(user_id):
        """Get comprehensive analysis statistics for a user"""
        try:
            # Basic counts
            total_analyses = AnalysisResult.query.filter_by(user_id=user_id).count()
            
            # Recent analyses (last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_analyses = AnalysisResult.query.filter(
                AnalysisResult.user_id == user_id,
                AnalysisResult.created_at >= thirty_days_ago
            ).count()
            
            # File type distribution
            file_type_stats = db.session.query(
                AnalysisResult.file_type,
                func.count(AnalysisResult.id).label('count')
            ).filter_by(user_id=user_id).group_by(AnalysisResult.file_type).all()
            
            file_type_distribution = {
                file_type: count for file_type, count in file_type_stats
            }
            
            # Monthly analysis trend (last 6 months)
            six_months_ago = datetime.utcnow() - timedelta(days=180)
            monthly_stats = db.session.query(
                func.date_trunc('month', AnalysisResult.created_at).label('month'),
                func.count(AnalysisResult.id).label('count')
            ).filter(
                AnalysisResult.user_id == user_id,
                AnalysisResult.created_at >= six_months_ago
            ).group_by('month').order_by('month').all()
            
            monthly_trend = [
                {
                    'month': month.strftime('%Y-%m') if month else 'Unknown',
                    'count': count
                }
                for month, count in monthly_stats
            ]
            
            # Get latest analysis for preview
            latest_analysis = AnalysisResult.query.filter_by(user_id=user_id).order_by(
                desc(AnalysisResult.created_at)
            ).first()
            
            latest_analysis_preview = None
            if latest_analysis:
                latest_analysis_preview = {
                    'id': latest_analysis.id,
                    'filename': latest_analysis.filename,
                    'created_at': latest_analysis.created_at.isoformat(),
                    'preview': latest_analysis.get_preview()
                }
            
            # Calculate average skills per analysis
            all_analyses = AnalysisResult.query.filter_by(user_id=user_id).all()
            total_skills = 0
            analyses_with_skills = 0
            
            for analysis in all_analyses:
                skills = analysis.get_extracted_skills()
                if skills:
                    total_skills += len(skills)
                    analyses_with_skills += 1
            
            avg_skills_per_analysis = (
                total_skills / analyses_with_skills if analyses_with_skills > 0 else 0
            )
            
            return {
                'success': True,
                'statistics': {
                    'total_analyses': total_analyses,
                    'recent_analyses': recent_analyses,
                    'file_type_distribution': file_type_distribution,
                    'monthly_trend': monthly_trend,
                    'average_skills_per_analysis': round(avg_skills_per_analysis, 1),
                    'latest_analysis': latest_analysis_preview,
                    'total_skills_analyzed': total_skills
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to calculate statistics: {str(e)}'
            }
    
    @staticmethod
    def get_global_statistics():
        """Get global platform statistics"""
        try:
            # Total analyses across all users
            total_analyses = AnalysisResult.query.count()
            
            # Total users
            total_users = User.query.count()
            
            # Active users (with at least one analysis)
            active_users = db.session.query(
                func.count(func.distinct(AnalysisResult.user_id))
            ).scalar()
            
            # Most common file types
            file_type_stats = db.session.query(
                AnalysisResult.file_type,
                func.count(AnalysisResult.id).label('count')
            ).group_by(AnalysisResult.file_type).order_by(desc('count')).limit(5).all()
            
            popular_file_types = [
                {'type': file_type, 'count': count}
                for file_type, count in file_type_stats
            ]
            
            # Recent activity (last 7 days)
            week_ago = datetime.utcnow() - timedelta(days=7)
            recent_activity = AnalysisResult.query.filter(
                AnalysisResult.created_at >= week_ago
            ).count()
            
            # Average analyses per user
            avg_analyses_per_user = total_analyses / max(active_users, 1)
            
            return {
                'success': True,
                'global_statistics': {
                    'total_analyses': total_analyses,
                    'total_users': total_users,
                    'active_users': active_users,
                    'popular_file_types': popular_file_types,
                    'recent_activity': recent_activity,
                    'average_analyses_per_user': round(avg_analyses_per_user, 1)
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to calculate global statistics: {str(e)}'
            }
    
    @staticmethod
    def search_analyses(user_id, query, search_type='all'):
        """Search through user's analyses"""
        try:
            # Base query
            base_query = AnalysisResult.query.filter_by(user_id=user_id)
            
            if search_type == 'filename':
                results = base_query.filter(
                    AnalysisResult.filename.ilike(f"%{query}%")
                ).all()
            elif search_type == 'skills':
                # Search in analysis data for skills
                results = []
                all_analyses = base_query.all()
                
                for analysis in all_analyses:
                    skills = analysis.get_extracted_skills()
                    if skills and any(query.lower() in skill.lower() for skill in skills):
                        results.append(analysis)
            else:  # search_type == 'all'
                # Search in filename and skills
                filename_results = base_query.filter(
                    AnalysisResult.filename.ilike(f"%{query}%")
                ).all()
                
                skill_results = []
                remaining_analyses = base_query.filter(
                    ~AnalysisResult.filename.ilike(f"%{query}%")
                ).all()
                
                for analysis in remaining_analyses:
                    skills = analysis.get_extracted_skills()
                    if skills and any(query.lower() in skill.lower() for skill in skills):
                        skill_results.append(analysis)
                
                results = filename_results + skill_results
            
            # Convert to dict format
            search_results = [result.to_dict() for result in results]
            
            return {
                'success': True,
                'results': search_results,
                'total_found': len(search_results),
                'query': query,
                'search_type': search_type
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Search failed: {str(e)}'
            }
    
    @staticmethod
    def export_analysis_data(user_id, analysis_ids=None):
        """Export analysis data for a user"""
        try:
            query = AnalysisResult.query.filter_by(user_id=user_id)
            
            if analysis_ids:
                query = query.filter(AnalysisResult.id.in_(analysis_ids))
            
            analyses = query.all()
            
            export_data = {
                'user_id': user_id,
                'export_date': datetime.utcnow().isoformat(),
                'total_analyses': len(analyses),
                'analyses': []
            }
            
            for analysis in analyses:
                analysis_dict = analysis.to_dict()
                # Include additional export-specific data
                analysis_dict['skills'] = analysis.get_extracted_skills()
                analysis_dict['match_percentage'] = analysis.get_match_percentage()
                export_data['analyses'].append(analysis_dict)
            
            return {
                'success': True,
                'export_data': export_data
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Export failed: {str(e)}'
            }