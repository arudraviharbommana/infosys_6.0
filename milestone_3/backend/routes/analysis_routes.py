"""
Analysis routes for skill analysis and result management
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from services.analysis_service import AnalysisService
from services.skill_service import SkillService
from services.file_service import FileService

analysis_bp = Blueprint('analysis', __name__, url_prefix='/api/analysis')

@analysis_bp.route('/analyze', methods=['POST'])
@login_required
def analyze_resume():
    """Analyze uploaded resume for skills using Ollama or fallback AI"""
    try:
        # Check if file is provided
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        job_description = request.form.get('job_description', '').strip()
        use_ollama = request.form.get('use_ollama', 'true').lower() == 'true'
        analysis_type = request.form.get('analysis_type', 'standard')  # standard, comprehensive
        
        # Process the uploaded file
        file_result = FileService.process_uploaded_file(file)
        
        if not file_result['success']:
            return jsonify(file_result), 400
        
        # Choose analysis method
        if analysis_type == 'comprehensive' and use_ollama:
            # Use comprehensive Ollama analysis
            comprehensive_result = SkillService.comprehensive_analysis_with_ollama(
                file_result['text'], job_description if job_description else None
            )
            
            if comprehensive_result['success']:
                analysis_data = {
                    'file_info': {
                        'filename': file_result['filename'],
                        'file_type': file_result['file_type'],
                        'file_size': file_result['file_size'],
                        'word_count': file_result['word_count'],
                        'char_count': file_result['char_count']
                    },
                    'extracted_text': file_result['text'],
                    'comprehensive_analysis': comprehensive_result['comprehensive_analysis'],
                    'job_description': job_description,
                    'processing_metadata': {
                        'extraction_method': 'ollama_comprehensive',
                        'confidence_level': 'high',
                        'processing_time': 'enhanced',
                        'analysis_type': 'comprehensive'
                    }
                }
                
                skill_result = comprehensive_result['comprehensive_analysis'].get('transformed_skills', {})
                response_data = {
                    'success': True,
                    'analysis_type': 'comprehensive',
                    'ollama_enhanced': True,
                    'file_info': analysis_data['file_info'],
                    'skills': skill_result.get('skills', []),
                    'categorized_skills': skill_result.get('categorized_skills', {}),
                    'insights': skill_result.get('insights', {}),
                    'total_skills': skill_result.get('total_skills', 0),
                    'comprehensive_analysis': comprehensive_result['comprehensive_analysis'],
                    'summary': comprehensive_result['summary'],
                    'message': 'Comprehensive analysis completed successfully'
                }
            else:
                # Fallback to standard analysis if comprehensive fails
                use_ollama = False
                analysis_type = 'standard'
        
        if analysis_type == 'standard' or not use_ollama:
            # Extract skills from the text
            skill_result = SkillService.extract_skills_from_text(
                file_result['text'], 
                job_description if job_description else None,
                use_ollama=use_ollama
            )
            
            if not skill_result['success']:
                return jsonify(skill_result), 500
            
            # Prepare analysis data
            analysis_data = {
                'file_info': {
                    'filename': file_result['filename'],
                    'file_type': file_result['file_type'],
                    'file_size': file_result['file_size'],
                    'word_count': file_result['word_count'],
                    'char_count': file_result['char_count']
                },
                'extracted_text': file_result['text'],
                'skills_analysis': skill_result,
                'job_description': job_description,
                'processing_metadata': {
                    'extraction_method': skill_result.get('analysis_method', 'custom_ai'),
                    'confidence_level': 'high',
                    'processing_time': 'real-time',
                    'analysis_type': 'standard'
                }
            }
            
            # Return standard analysis result
            response_data = {
                'success': True,
                'analysis_type': 'standard',
                'ollama_enhanced': skill_result.get('analysis_method') == 'ollama_enhanced',
                'file_info': analysis_data['file_info'],
                'skills': skill_result['skills'],
                'categorized_skills': skill_result['categorized_skills'],
                'insights': skill_result['insights'],
                'total_skills': skill_result['total_skills'],
                'message': 'Analysis completed successfully'
            }
            
            # Include job matching if job description was provided
            if job_description and 'job_matching' in skill_result:
                response_data['job_matching'] = skill_result['job_matching']
            
            # Include Ollama-specific data if available
            if 'ollama_analysis' in skill_result:
                response_data['ollama_analysis'] = skill_result['ollama_analysis']
            
            if 'career_recommendations' in skill_result:
                response_data['career_recommendations'] = skill_result['career_recommendations']
            
            if 'quality_analysis' in skill_result:
                response_data['quality_analysis'] = skill_result['quality_analysis']
        
        # Save analysis result
        save_result = AnalysisService.save_analysis_result(
            user_id=current_user.id,
            analysis_data=analysis_data,
            filename=file_result['filename'],
            file_type=file_result['file_type']
        )
        
        if save_result['success']:
            response_data['analysis_id'] = save_result['analysis']['id']
        
        return jsonify(response_data), 201
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Analysis failed: {str(e)}'}), 500

@analysis_bp.route('/match-job', methods=['POST'])
@login_required
def match_job():
    """Match skills to a job description"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        analysis_id = data.get('analysis_id')
        job_description = data.get('job_description', '').strip()
        
        if not analysis_id:
            return jsonify({'success': False, 'error': 'Analysis ID is required'}), 400
        
        if not job_description:
            return jsonify({'success': False, 'error': 'Job description is required'}), 400
        
        # Get the analysis
        analysis_result = AnalysisService.get_analysis_by_id(analysis_id, current_user.id)
        
        if not analysis_result['success']:
            return jsonify(analysis_result), 404
        
        analysis = analysis_result['analysis']
        
        # Extract skills from the analysis
        skills = []
        if 'skills_analysis' in analysis['analysis_data']:
            skills = analysis['analysis_data']['skills_analysis'].get('skills', [])
        
        if not skills:
            return jsonify({'success': False, 'error': 'No skills found in analysis'}), 400
        
        # Match skills to job
        matching_result = SkillService.match_skills_to_job(skills, job_description)
        
        if not matching_result['success']:
            return jsonify(matching_result), 500
        
        return jsonify({
            'success': True,
            'analysis_id': analysis_id,
            'job_matching': matching_result['matching'],
            'message': 'Job matching completed successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Job matching failed: {str(e)}'}), 500

@analysis_bp.route('/history', methods=['GET'])
@login_required
def get_analysis_history():
    """Get user's analysis history with pagination and filtering"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 50)
        search = request.args.get('search', '').strip()
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        
        # Validate sort parameters
        valid_sort_fields = ['created_at', 'filename', 'file_type']
        if sort_by not in valid_sort_fields:
            sort_by = 'created_at'
        
        if sort_order not in ['asc', 'desc']:
            sort_order = 'desc'
        
        result = AnalysisService.get_user_analyses(
            user_id=current_user.id,
            page=page,
            per_page=per_page,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to get analysis history: {str(e)}'}), 500

@analysis_bp.route('/<int:analysis_id>', methods=['GET'])
@login_required
def get_analysis_details(analysis_id):
    """Get detailed analysis results"""
    try:
        result = AnalysisService.get_analysis_by_id(analysis_id, current_user.id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to get analysis details: {str(e)}'}), 500

@analysis_bp.route('/<int:analysis_id>', methods=['DELETE'])
@login_required
def delete_analysis(analysis_id):
    """Delete an analysis"""
    try:
        result = AnalysisService.delete_analysis(analysis_id, current_user.id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404 if 'not found' in result.get('error', '').lower() else 500
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to delete analysis: {str(e)}'}), 500

@analysis_bp.route('/statistics', methods=['GET'])
@login_required
def get_analysis_statistics():
    """Get comprehensive analysis statistics for the user"""
    try:
        result = AnalysisService.get_user_analysis_statistics(current_user.id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to get statistics: {str(e)}'}), 500

@analysis_bp.route('/export', methods=['GET'])
@login_required
def export_analyses():
    """Export user's analysis data"""
    try:
        # Get analysis IDs from query params (optional)
        analysis_ids_param = request.args.get('ids', '')
        analysis_ids = None
        
        if analysis_ids_param:
            try:
                analysis_ids = [int(id_str.strip()) for id_str in analysis_ids_param.split(',') if id_str.strip()]
            except ValueError:
                return jsonify({'success': False, 'error': 'Invalid analysis IDs provided'}), 400
        
        result = AnalysisService.export_analysis_data(current_user.id, analysis_ids)
        
        if result['success']:
            from flask import Response
            import json
            
            response = Response(
                json.dumps(result['export_data'], indent=2, default=str),
                mimetype='application/json'
            )
            response.headers['Content-Disposition'] = f'attachment; filename=analyses_export_{current_user.id}.json'
            return response
        else:
            return jsonify(result), 500
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Export failed: {str(e)}'}), 500

@analysis_bp.route('/search', methods=['GET'])
@login_required
def search_analyses():
    """Search through user's analyses"""
    try:
        query = request.args.get('q', '').strip()
        search_type = request.args.get('type', 'all')  # all, filename, skills
        
        if not query:
            return jsonify({'success': False, 'error': 'Search query is required'}), 400
        
        if len(query) < 2:
            return jsonify({'success': False, 'error': 'Search query must be at least 2 characters'}), 400
        
        valid_search_types = ['all', 'filename', 'skills']
        if search_type not in valid_search_types:
            search_type = 'all'
        
        result = AnalysisService.search_analyses(current_user.id, query, search_type)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Search failed: {str(e)}'}), 500

@analysis_bp.route('/reanalyze/<int:analysis_id>', methods=['POST'])
@login_required
def reanalyze_with_job(analysis_id):
    """Re-analyze existing analysis with new job description"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        job_description = data.get('job_description', '').strip()
        
        if not job_description:
            return jsonify({'success': False, 'error': 'Job description is required'}), 400
        
        # Get the existing analysis
        analysis_result = AnalysisService.get_analysis_by_id(analysis_id, current_user.id)
        
        if not analysis_result['success']:
            return jsonify(analysis_result), 404
        
        analysis = analysis_result['analysis']
        
        # Extract original text and skills
        analysis_data = analysis['analysis_data']
        original_text = analysis_data.get('extracted_text', '')
        original_skills = []
        
        if 'skills_analysis' in analysis_data:
            original_skills = analysis_data['skills_analysis'].get('skills', [])
        
        if not original_text or not original_skills:
            return jsonify({'success': False, 'error': 'Original analysis data incomplete'}), 400
        
        # Re-run skill analysis with job description
        skill_result = SkillService.extract_skills_from_text(original_text, job_description)
        
        if not skill_result['success']:
            return jsonify(skill_result), 500
        
        # Update analysis data
        updated_analysis_data = analysis_data.copy()
        updated_analysis_data['skills_analysis'] = skill_result
        updated_analysis_data['job_description'] = job_description
        updated_analysis_data['reanalyzed_at'] = datetime.utcnow().isoformat()
        
        # Save as new analysis
        save_result = AnalysisService.save_analysis_result(
            user_id=current_user.id,
            analysis_data=updated_analysis_data,
            filename=f"Reanalyzed - {analysis['filename']}",
            file_type=analysis['file_type']
        )
        
        if save_result['success']:
            return jsonify({
                'success': True,
                'new_analysis_id': save_result['analysis']['id'],
                'skills': skill_result['skills'],
                'job_matching': skill_result.get('job_matching', {}),
                'message': 'Re-analysis completed successfully'
            }), 201
        else:
            return jsonify(save_result), 500
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Re-analysis failed: {str(e)}'}), 500

@analysis_bp.route('/comprehensive-analyze', methods=['POST'])
@login_required
def comprehensive_analyze():
    """Perform comprehensive analysis using Ollama for advanced insights"""
    try:
        # Check if file is provided
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        job_description = request.form.get('job_description', '').strip()
        
        # Process the uploaded file
        file_result = FileService.process_uploaded_file(file)
        
        if not file_result['success']:
            return jsonify(file_result), 400
        
        # Perform comprehensive analysis with Ollama
        comprehensive_result = SkillService.comprehensive_analysis_with_ollama(
            file_result['text'], 
            job_description if job_description else None
        )
        
        if not comprehensive_result['success']:
            return jsonify(comprehensive_result), 500
        
        # Prepare comprehensive analysis data
        analysis_data = {
            'file_info': {
                'filename': file_result['filename'],
                'file_type': file_result['file_type'],
                'file_size': file_result['file_size'],
                'word_count': file_result['word_count'],
                'char_count': file_result['char_count']
            },
            'extracted_text': file_result['text'],
            'comprehensive_analysis': comprehensive_result['comprehensive_analysis'],
            'job_description': job_description,
            'processing_metadata': {
                'extraction_method': 'ollama_comprehensive',
                'confidence_level': 'high',
                'processing_time': 'enhanced',
                'analysis_type': 'comprehensive'
            }
        }
        
        # Save analysis result
        save_result = AnalysisService.save_analysis_result(
            user_id=current_user.id,
            analysis_data=analysis_data,
            filename=file_result['filename'],
            file_type=file_result['file_type']
        )
        
        if not save_result['success']:
            return jsonify(save_result), 500
        
        # Return comprehensive response
        response_data = {
            'success': True,
            'analysis_id': save_result['analysis']['id'],
            'analysis_type': 'comprehensive',
            'ollama_enhanced': True,
            'file_info': analysis_data['file_info'],
            'comprehensive_analysis': comprehensive_result['comprehensive_analysis'],
            'summary': comprehensive_result['summary'],
            'message': 'Comprehensive analysis completed successfully'
        }
        
        return jsonify(response_data), 201
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Comprehensive analysis failed: {str(e)}'}), 500

@analysis_bp.route('/ollama-status', methods=['GET'])
@login_required
def get_ollama_status():
    """Check Ollama service status and available models"""
    try:
        from services.ollama_service import OllamaService
        
        ollama_service = OllamaService()
        status_result = ollama_service.check_model_availability()
        
        return jsonify({
            'success': True,
            'ollama_status': status_result,
            'recommended_model': ollama_service.model,
            'service_url': ollama_service.base_url
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to check Ollama status: {str(e)}',
            'ollama_available': False
        }), 200

@analysis_bp.route('/quality-check', methods=['POST'])
@login_required
def analyze_resume_quality():
    """Analyze resume quality using Ollama"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        # Process the uploaded file
        file_result = FileService.process_uploaded_file(file)
        
        if not file_result['success']:
            return jsonify(file_result), 400
        
        # Analyze quality with Ollama
        from services.ollama_service import OllamaService
        ollama_service = OllamaService()
        
        quality_result = ollama_service.analyze_resume_quality(file_result['text'])
        
        if not quality_result['success']:
            return jsonify(quality_result), 500
        
        return jsonify({
            'success': True,
            'file_info': {
                'filename': file_result['filename'],
                'file_type': file_result['file_type'],
                'word_count': file_result['word_count']
            },
            'quality_analysis': quality_result['quality_analysis'],
            'message': 'Quality analysis completed successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Quality analysis failed: {str(e)}'}), 500

@analysis_bp.route('/bulk-delete', methods=['DELETE'])
@login_required
def bulk_delete_analyses():
    """Delete multiple analyses"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        analysis_ids = data.get('analysis_ids', [])
        
        if not analysis_ids or not isinstance(analysis_ids, list):
            return jsonify({'success': False, 'error': 'Analysis IDs must be provided as a list'}), 400
        
        if len(analysis_ids) > 100:  # Limit bulk operations
            return jsonify({'success': False, 'error': 'Cannot delete more than 100 analyses at once'}), 400
        
        results = []
        successful_deletions = 0
        
        for analysis_id in analysis_ids:
            try:
                result = AnalysisService.delete_analysis(int(analysis_id), current_user.id)
                results.append({
                    'analysis_id': analysis_id,
                    'success': result['success'],
                    'error': result.get('error')
                })
                if result['success']:
                    successful_deletions += 1
            except ValueError:
                results.append({
                    'analysis_id': analysis_id,
                    'success': False,
                    'error': 'Invalid analysis ID'
                })
        
        return jsonify({
            'success': True,
            'results': results,
            'successful_deletions': successful_deletions,
            'total_requested': len(analysis_ids),
            'message': f'Bulk deletion completed. {successful_deletions}/{len(analysis_ids)} analyses deleted successfully.'
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Bulk deletion failed: {str(e)}'}), 500