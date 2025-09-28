"""
File processing routes for upload validation and text extraction
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required
from services.file_service import FileService

file_bp = Blueprint('file', __name__, url_prefix='/api/file')

@file_bp.route('/validate', methods=['POST'])
@login_required
def validate_file():
    """Validate uploaded file without processing"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        result = FileService.validate_file(file)
        
        if result['success']:
            # Get additional file info
            filename = file.filename
            file_size = file.seek(0, 2)  # Seek to end to get size
            file.seek(0)  # Reset position
            
            return jsonify({
                'success': True,
                'valid': True,
                'filename': filename,
                'file_size': file_size,
                'file_type': filename.rsplit('.', 1)[1].lower() if '.' in filename else 'unknown',
                'message': 'File is valid for processing'
            }), 200
        else:
            return jsonify({
                'success': True,
                'valid': False,
                'error': result['error']
            }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'File validation failed: {str(e)}'}), 500

@file_bp.route('/extract-text', methods=['POST'])
@login_required
def extract_text():
    """Extract text from uploaded file"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        result = FileService.process_uploaded_file(file)
        
        if result['success']:
            # Clean the extracted text
            clean_result = FileService.clean_extracted_text(result['text'])
            
            if clean_result['success']:
                result['cleaned_text'] = clean_result['cleaned_text']
            
            # Get text preview
            preview = FileService.get_file_preview(result['text'], max_length=300)
            result['preview'] = preview
            
            return jsonify(result), 200
        else:
            return jsonify(result), 400
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Text extraction failed: {str(e)}'}), 500

@file_bp.route('/supported-formats', methods=['GET'])
def get_supported_formats():
    """Get list of supported file formats"""
    try:
        formats = list(FileService.ALLOWED_EXTENSIONS)
        max_size_mb = FileService.MAX_FILE_SIZE // (1024 * 1024)
        
        format_details = {
            'pdf': {
                'description': 'Portable Document Format',
                'common_use': 'Resumes, CVs, documents',
                'notes': 'Supports both text-based and image-based PDFs'
            },
            'txt': {
                'description': 'Plain Text Format',
                'common_use': 'Simple text documents',
                'notes': 'Supports various text encodings'
            }
        }
        
        return jsonify({
            'success': True,
            'supported_formats': formats,
            'max_file_size_mb': max_size_mb,
            'format_details': format_details,
            'processing_capabilities': [
                'Text extraction from PDFs',
                'Multi-encoding text file support',
                'Automatic content cleaning',
                'Text preview generation'
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to get supported formats: {str(e)}'}), 500

@file_bp.route('/preview', methods=['POST'])
@login_required
def get_file_preview():
    """Get preview of file content without full processing"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        preview_length = request.form.get('preview_length', 500, type=int)
        
        # Limit preview length
        preview_length = min(max(preview_length, 100), 2000)
        
        # Validate file first
        validation_result = FileService.validate_file(file)
        if not validation_result['success']:
            return jsonify(validation_result), 400
        
        # Extract text
        extraction_result = FileService.process_uploaded_file(file)
        if not extraction_result['success']:
            return jsonify(extraction_result), 400
        
        # Get preview
        preview = FileService.get_file_preview(extraction_result['text'], preview_length)
        
        return jsonify({
            'success': True,
            'filename': extraction_result['filename'],
            'file_type': extraction_result['file_type'],
            'preview': preview,
            'full_length': len(extraction_result['text']),
            'preview_length': len(preview),
            'word_count': extraction_result['word_count'],
            'is_truncated': len(extraction_result['text']) > preview_length
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Preview generation failed: {str(e)}'}), 500

@file_bp.route('/analyze-content', methods=['POST'])
@login_required
def analyze_file_content():
    """Analyze file content structure and properties"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        # Process file
        result = FileService.process_uploaded_file(file)
        if not result['success']:
            return jsonify(result), 400
        
        text = result['text']
        
        # Analyze content structure
        lines = text.split('\n')
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        sentences = [s.strip() for s in text.replace('\n', ' ').split('.') if s.strip()]
        words = text.split()
        
        # Analyze content type (simple heuristics)
        content_indicators = {
            'resume_indicators': [
                'experience', 'education', 'skills', 'objective', 'summary',
                'work history', 'employment', 'qualifications', 'achievements'
            ],
            'technical_indicators': [
                'programming', 'software', 'development', 'technical', 'coding',
                'database', 'framework', 'language', 'technology'
            ],
            'contact_indicators': [
                'email', 'phone', 'address', 'linkedin', 'github', 'website'
            ]
        }
        
        text_lower = text.lower()
        content_analysis = {}
        
        for category, indicators in content_indicators.items():
            matches = sum(1 for indicator in indicators if indicator in text_lower)
            content_analysis[category] = {
                'matches': matches,
                'percentage': (matches / len(indicators)) * 100
            }
        
        # Determine likely document type
        resume_score = content_analysis['resume_indicators']['percentage']
        technical_score = content_analysis['technical_indicators']['percentage']
        
        if resume_score >= 30:
            document_type = 'resume/cv'
            confidence = 'high' if resume_score >= 50 else 'medium'
        elif technical_score >= 40:
            document_type = 'technical_document'
            confidence = 'medium'
        else:
            document_type = 'general_document'
            confidence = 'low'
        
        return jsonify({
            'success': True,
            'file_info': {
                'filename': result['filename'],
                'file_type': result['file_type'],
                'file_size': result['file_size']
            },
            'content_stats': {
                'total_characters': len(text),
                'total_words': len(words),
                'total_sentences': len(sentences),
                'total_paragraphs': len(paragraphs),
                'total_lines': len(lines),
                'average_words_per_sentence': len(words) / max(len(sentences), 1),
                'average_sentences_per_paragraph': len(sentences) / max(len(paragraphs), 1)
            },
            'content_analysis': content_analysis,
            'document_classification': {
                'type': document_type,
                'confidence': confidence,
                'technical_content': technical_score >= 20
            },
            'readability': {
                'complexity': 'high' if len(words) / max(len(sentences), 1) > 20 else 'medium' if len(words) / max(len(sentences), 1) > 15 else 'low',
                'structure_quality': 'good' if len(paragraphs) > 3 else 'fair'
            }
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Content analysis failed: {str(e)}'}), 500

@file_bp.route('/batch-validate', methods=['POST'])
@login_required
def batch_validate_files():
    """Validate multiple files at once"""
    try:
        files = request.files.getlist('files')
        
        if not files:
            return jsonify({'success': False, 'error': 'No files provided'}), 400
        
        if len(files) > 10:  # Limit batch size
            return jsonify({'success': False, 'error': 'Cannot validate more than 10 files at once'}), 400
        
        results = []
        valid_count = 0
        
        for i, file in enumerate(files):
            try:
                validation_result = FileService.validate_file(file)
                
                file_result = {
                    'index': i,
                    'filename': file.filename,
                    'valid': validation_result['success'],
                    'error': validation_result.get('error') if not validation_result['success'] else None
                }
                
                if validation_result['success']:
                    valid_count += 1
                    # Get file size
                    file.seek(0, 2)
                    file_size = file.tell()
                    file.seek(0)
                    
                    file_result['file_size'] = file_size
                    file_result['file_type'] = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'unknown'
                
                results.append(file_result)
                
            except Exception as e:
                results.append({
                    'index': i,
                    'filename': file.filename if hasattr(file, 'filename') else f'file_{i}',
                    'valid': False,
                    'error': f'Validation error: {str(e)}'
                })
        
        return jsonify({
            'success': True,
            'results': results,
            'summary': {
                'total_files': len(files),
                'valid_files': valid_count,
                'invalid_files': len(files) - valid_count,
                'validation_rate': (valid_count / len(files)) * 100
            }
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Batch validation failed: {str(e)}'}), 500