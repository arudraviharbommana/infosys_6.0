
# ...existing code...

user_bp = Blueprint('user', __name__, url_prefix='/api/user')

@user_bp.route('', methods=['GET'])
@login_required
def get_user():
    """Get current user profile (for /api/user)"""
    try:
        result = AuthService.get_user_profile(current_user.id)
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to get user: {str(e)}'}), 500
"""
User routes for profile management and user-related operations
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from services.auth_service import AuthService
from services.analysis_service import AnalysisService

user_bp = Blueprint('user', __name__, url_prefix='/api/user')

@user_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    """Get user profile with comprehensive data"""
    try:
        result = AuthService.get_user_profile(current_user.id)
        
        if result['success']:
            # Add analysis statistics to profile
            stats_result = AnalysisService.get_user_analysis_statistics(current_user.id)
            if stats_result['success']:
                result['profile']['analysis_statistics'] = stats_result['statistics']
            
            return jsonify(result), 200
        else:
            return jsonify(result), 404
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to get profile: {str(e)}'}), 500

@user_bp.route('/stats', methods=['GET'])
@login_required
def get_user_stats():
    """Get detailed user statistics"""
    try:
        result = AnalysisService.get_user_analysis_statistics(current_user.id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to get statistics: {str(e)}'}), 500

@user_bp.route('/dashboard', methods=['GET'])
@login_required
def get_dashboard_data():
    """Get comprehensive dashboard data for user"""
    try:
        # Get user profile
        profile_result = AuthService.get_user_profile(current_user.id)
        if not profile_result['success']:
            return jsonify(profile_result), 404
        
        # Get analysis statistics
        stats_result = AnalysisService.get_user_analysis_statistics(current_user.id)
        if not stats_result['success']:
            return jsonify(stats_result), 500
        
        # Get recent analyses (last 5)
        recent_analyses_result = AnalysisService.get_user_analyses(
            current_user.id, page=1, per_page=5, sort_by='created_at', sort_order='desc'
        )
        
        dashboard_data = {
            'user': profile_result['profile']['user'],
            'achievements': profile_result['profile']['achievements'],
            'statistics': stats_result['statistics'],
            'recent_analyses': recent_analyses_result.get('analyses', []) if recent_analyses_result['success'] else []
        }
        
        return jsonify({
            'success': True,
            'dashboard': dashboard_data
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to get dashboard data: {str(e)}'}), 500

@user_bp.route('/preferences', methods=['GET'])
@login_required
def get_preferences():
    """Get user preferences (placeholder for future implementation)"""
    try:
        # Placeholder for user preferences
        preferences = {
            'theme': 'light',
            'notifications': True,
            'privacy_level': 'medium',
            'export_format': 'json'
        }
        
        return jsonify({
            'success': True,
            'preferences': preferences
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to get preferences: {str(e)}'}), 500

@user_bp.route('/preferences', methods=['PUT'])
@login_required
def update_preferences():
    """Update user preferences (placeholder for future implementation)"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Placeholder - in a real implementation, you'd save these to the database
        allowed_preferences = ['theme', 'notifications', 'privacy_level', 'export_format']
        
        updated_preferences = {}
        for key, value in data.items():
            if key in allowed_preferences:
                updated_preferences[key] = value
        
        if not updated_preferences:
            return jsonify({'success': False, 'error': 'No valid preferences provided'}), 400
        
        return jsonify({
            'success': True,
            'message': 'Preferences updated successfully',
            'preferences': updated_preferences
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to update preferences: {str(e)}'}), 500

@user_bp.route('/activity', methods=['GET'])
@login_required
def get_user_activity():
    """Get user activity log (recent actions)"""
    try:
        # Get recent analyses as activity
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 50)
        
        result = AnalysisService.get_user_analyses(
            current_user.id, 
            page=page, 
            per_page=per_page,
            sort_by='created_at',
            sort_order='desc'
        )
        
        if result['success']:
            # Format as activity items
            activities = []
            for analysis in result['analyses']:
                activities.append({
                    'id': analysis['id'],
                    'type': 'analysis',
                    'action': 'created',
                    'description': f"Analyzed {analysis['filename'] or 'document'}",
                    'timestamp': analysis['created_at'],
                    'metadata': {
                        'filename': analysis['filename'],
                        'file_type': analysis['file_type'],
                        'skills_count': len(analysis.get('skills', [])) if 'skills' in analysis else 0
                    }
                })
            
            return jsonify({
                'success': True,
                'activities': activities,
                'pagination': result['pagination']
            }), 200
        else:
            return jsonify(result), 500
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to get activity: {str(e)}'}), 500

@user_bp.route('/export', methods=['GET'])
@login_required
def export_user_data():
    """Export all user data"""
    try:
        # Get export format from query params
        export_format = request.args.get('format', 'json').lower()
        
        if export_format not in ['json', 'csv']:
            return jsonify({'success': False, 'error': 'Unsupported export format'}), 400
        
        # Export analysis data
        result = AnalysisService.export_analysis_data(current_user.id)
        
        if not result['success']:
            return jsonify(result), 500
        
        export_data = result['export_data']
        
        # Add user profile data
        profile_result = AuthService.get_user_profile(current_user.id)
        if profile_result['success']:
            export_data['user_profile'] = profile_result['profile']
        
        if export_format == 'json':
            from flask import Response
            import json
            
            response = Response(
                json.dumps(export_data, indent=2, default=str),
                mimetype='application/json'
            )
            response.headers['Content-Disposition'] = f'attachment; filename=user_data_{current_user.id}.json'
            return response
        
        elif export_format == 'csv':
            # Convert to CSV format (simplified)
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow(['ID', 'Filename', 'File Type', 'Created At', 'Skills Count', 'Match Percentage'])
            
            # Write data
            for analysis in export_data['analyses']:
                writer.writerow([
                    analysis['id'],
                    analysis['filename'],
                    analysis['file_type'],
                    analysis['created_at'],
                    len(analysis.get('skills', [])),
                    analysis.get('match_percentage', 0)
                ])
            
            output.seek(0)
            
            from flask import Response
            response = Response(output.getvalue(), mimetype='text/csv')
            response.headers['Content-Disposition'] = f'attachment; filename=user_data_{current_user.id}.csv'
            return response
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Export failed: {str(e)}'}), 500

@user_bp.route('/search', methods=['GET'])
@login_required
def search_user_content():
    """Search through user's content"""
    try:
        query = request.args.get('q', '').strip()
        search_type = request.args.get('type', 'all')  # all, filename, skills
        
        if not query:
            return jsonify({'success': False, 'error': 'Search query is required'}), 400
        
        if len(query) < 2:
            return jsonify({'success': False, 'error': 'Search query must be at least 2 characters'}), 400
        
        result = AnalysisService.search_analyses(current_user.id, query, search_type)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Search failed: {str(e)}'}), 500

@user_bp.route('/notifications', methods=['GET'])
@login_required
def get_notifications():
    """Get user notifications (placeholder for future implementation)"""
    try:
        # Placeholder notifications based on user activity
        notifications = []
        
        # Check if user has recent analyses
        recent_result = AnalysisService.get_user_analyses(
            current_user.id, page=1, per_page=1, sort_by='created_at', sort_order='desc'
        )
        
        if recent_result['success'] and recent_result['analyses']:
            last_analysis = recent_result['analyses'][0]
            from datetime import datetime, timedelta
            
            # If last analysis was more than 7 days ago, suggest creating a new one
            created_at = datetime.fromisoformat(last_analysis['created_at'].replace('Z', '+00:00'))
            if (datetime.utcnow() - created_at.replace(tzinfo=None)) > timedelta(days=7):
                notifications.append({
                    'id': 'suggest_analysis',
                    'type': 'suggestion',
                    'title': 'Time for a new analysis?',
                    'message': 'It\'s been a while since your last skill analysis. Upload a new resume to track your progress!',
                    'timestamp': datetime.utcnow().isoformat(),
                    'read': False
                })
        
        return jsonify({
            'success': True,
            'notifications': notifications,
            'unread_count': len([n for n in notifications if not n.get('read', True)])
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to get notifications: {str(e)}'}), 500