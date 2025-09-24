# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import sys
import os
import PyPDF2
import pdfplumber
import io

# Add the parent directory to the path to import custom_ai
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from custom_ai import CustomSkillExtractor, CustomJobMatcher

app = Flask(__name__)
CORS(app)  # Enables CORS for cross-origin requests from the React frontend

# Initialize our custom AI components
skill_extractor = CustomSkillExtractor()
job_matcher = CustomJobMatcher()

def extract_text_from_pdf(pdf_file):
    """Extract text from PDF file using multiple methods for better accuracy"""
    text = ""
    
    try:
        # Method 1: Try pdfplumber first (better for complex layouts)
        pdf_file.seek(0)  # Reset file pointer
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        # If pdfplumber didn't extract much text, try PyPDF2
        if len(text.strip()) < 50:
            pdf_file.seek(0)  # Reset file pointer
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    
    except Exception as e:
        print(f"Error extracting text from PDF: {str(e)}")
        return None
    
    return text.strip() if text.strip() else None

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'AI-Free Skill Matcher API is running'}), 200

@app.route('/api/match', methods=['POST'])
def match_skills():
    """
    API endpoint to match a resume against a job description.
    Supports both text and PDF inputs.
    """
    try:
        # Check if request contains files (PDF uploads)
        if 'resume_file' in request.files or 'job_file' in request.files:
            resume_text = ""
            job_description = ""
            
            # Handle resume file
            if 'resume_file' in request.files:
                resume_file = request.files['resume_file']
                if resume_file.filename != '':
                    if resume_file.filename.lower().endswith('.pdf'):
                        resume_text = extract_text_from_pdf(resume_file)
                        if not resume_text:
                            return jsonify({'error': 'Could not extract text from resume PDF. Please try uploading a text file or typing the content manually.'}), 400
                    else:
                        # Handle text files
                        resume_text = resume_file.read().decode('utf-8')
            
            # Handle job description file
            if 'job_file' in request.files:
                job_file = request.files['job_file']
                if job_file.filename != '':
                    if job_file.filename.lower().endswith('.pdf'):
                        job_description = extract_text_from_pdf(job_file)
                        if not job_description:
                            return jsonify({'error': 'Could not extract text from job description PDF. Please try uploading a text file or typing the content manually.'}), 400
                    else:
                        # Handle text files
                        job_description = job_file.read().decode('utf-8')
            
            # Get any additional text from form data
            form_data = request.form
            if 'resumeText' in form_data and form_data['resumeText'].strip():
                resume_text += "\n" + form_data['resumeText']
            if 'jobDescription' in form_data and form_data['jobDescription'].strip():
                job_description += "\n" + form_data['jobDescription']
                
        else:
            # Handle JSON request (text only)
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided. Please provide either text or upload files.'}), 400
            
            resume_text = data.get('resumeText', '')
            job_description = data.get('jobDescription', '')

        # Validate that we have both resume and job description
        if not resume_text or not job_description:
            return jsonify({'error': 'Both resume and job description are required. Please provide text or upload files for both.'}), 400

        # Extract skills from both texts using the CustomSkillExtractor
        resume_analysis = skill_extractor.extract_skills_from_text(resume_text)
        job_analysis = skill_extractor.extract_skills_from_text(job_description)

        # The main score calculation now includes the comparison view
        match_results = job_matcher.calculate_match_score(resume_text, job_description)

        # The learning path is now part of the main match results
        learning_path = match_results.get('recommendations', [])
        
        # Combine all results into a single response
        # We can simplify the response if we only need the comparison for now
        # but let's keep the rich data structure
        response_data = {
            'match_summary': {
                'overall_score': match_results['overall_score'],
                'detailed_scores': match_results['detailed_scores']
            },
            'skills_analysis': {
                'resume_skills': list(resume_analysis['skills'].keys()),
                'job_skills': list(job_analysis['skills'].keys()),
                'matched_skills': match_results['matched_skills'],
                'missing_skills': match_results['missing_skills'],
                'extra_skills': match_results['extra_skills']
            },
            'comparison': match_results.get('comparison', []), # The new detailed comparison
            'skill_gaps': match_results['skill_gaps'],
            'learning_path_recommendations': learning_path,
            'experience_analysis': {
                'resume_experience': resume_analysis['experience'],
                'job_experience': job_analysis['experience']
            },
            'category_breakdown': {
                'resume_categories': resume_analysis['categories'],
                'job_categories': job_analysis['categories'],
                'resume_top_categories': resume_analysis['top_categories'],
                'job_top_categories': job_analysis['top_categories']
            },
            'extracted_text_info': {
                'resume_text_length': len(resume_text),
                'job_text_length': len(job_description),
                'resume_preview': resume_text[:200] + "..." if len(resume_text) > 200 else resume_text,
                'job_preview': job_description[:200] + "..." if len(job_description) > 200 else job_description
            }
        }

        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({'error': f'An error occurred while processing your request: {str(e)}'}), 500

@app.route('/api/extract-pdf', methods=['POST'])
def extract_pdf_text():
    """
    API endpoint to extract text from a PDF file.
    """
    try:
        if 'pdf_file' not in request.files:
            return jsonify({'error': 'No PDF file provided'}), 400
        
        pdf_file = request.files['pdf_file']
        
        if pdf_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not pdf_file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'File must be a PDF'}), 400
        
        extracted_text = extract_text_from_pdf(pdf_file)
        
        if not extracted_text:
            return jsonify({'error': 'Could not extract text from PDF. The PDF might be image-based or corrupted.'}), 400
        
        # Analyze the extracted text
        analysis = skill_extractor.extract_skills_from_text(extracted_text)
        
        return jsonify({
            'extracted_text': extracted_text,
            'text_length': len(extracted_text),
            'word_count': len(extracted_text.split()),
            'skills_found': len(analysis['skills']),
            'preview': extracted_text[:300] + "..." if len(extracted_text) > 300 else extracted_text,
            'analysis': analysis
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error processing PDF: {str(e)}'}), 500

@app.route('/api/extract-skills', methods=['POST'])
def extract_skills():
    """
    API endpoint to extract skills from a single text (resume or job description).
    """
    data = request.get_json()
    text = data.get('text', '')

    if not text:
        return jsonify({'error': 'Text is required.'}), 400

    try:
        analysis = skill_extractor.extract_skills_from_text(text)
        return jsonify(analysis), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # You might want to change this for production
    app.run(debug=True, port=5000)