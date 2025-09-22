"""
Advanced Skill Matching Backend with Custom AI-Free Algorithms
Provides intelligent skill matching between resumes and job descriptions
using rule-based algorithms and fuzzy matching.
"""

import os
import logging
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import our custom AI-free skill matching system
from custom_ai import CustomSkillExtractor, CustomJobMatcher, CustomRecommendationEngine

# Configure logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
try:
    from dotenv import load_dotenv
    # Load .env file from the same directory as this script
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        logger.info(f"✅ Loaded environment from: {env_path}")
    else:
        logger.warning(f"⚠️ No .env file found at: {env_path}")
except ImportError:
    logger.warning("⚠️ python-dotenv not installed. Using system environment variables only")

# Import PDF processing
try:
    import fitz  # PyMuPDF for PDF processing
    logger.info("✅ PyMuPDF imported successfully")
except ImportError as e:
    logger.error(f"❌ Error importing PyMuPDF: {e}")
    logger.error("📦 Install with: pip install PyMuPDF")
    exit(1)

# Duplicate section removed - configuration handled above

# Initialize Flask app
app = Flask(__name__)

# Get configuration from environment
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 5001))
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
DEBUG_MODE = os.getenv('DEBUG_MODE', 'true').lower() == 'true'

# Configure CORS to allow frontend connections
cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
# Add dynamic host-based origins
cors_origins.extend([
    f"http://{HOST}:3000",
    f"http://{HOST}:3001"
])
CORS(app, origins=cors_origins, supports_credentials=True, allow_headers=['Content-Type', 'Authorization'])

# Security configurations
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_FILE_SIZE_MB', 10)) * 1024 * 1024  # 10MB default
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'd2fd3661ab4671d74b6f9533c5c1cbb57eb7840be230aa260db41f6e09f4d1d0')

# Initialize our custom AI-free components
skill_extractor = CustomSkillExtractor()
job_matcher = CustomJobMatcher()
recommendation_engine = CustomRecommendationEngine()

# Get configuration from environment
FUZZY_THRESHOLD = float(os.getenv('FUZZY_MATCH_THRESHOLD', 0.8))
CONFIDENCE_THRESHOLD = float(os.getenv('CONFIDENCE_THRESHOLD', 0.6))
APP_VERSION = os.getenv('APP_VERSION', '3.0.0-custom')

logger.info("✅ Custom AI-free skill matching system initialized")

# Helper functions using our custom AI-free system
def extract_text_from_pdf(pdf_stream) -> str:
    """Extract text from PDF file stream."""
    try:
        pdf_stream.seek(0)  # Reset stream position
        doc = fitz.open(stream=pdf_stream.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        return ""

def process_resume_analysis(resume_text: str, job_description: str = "") -> Dict[str, Any]:
    """Process resume using custom AI-free analysis."""
    try:
        # Extract skills from resume
        resume_analysis = skill_extractor.extract_skills_from_text(resume_text)
        
        result = {
            "skills_found": resume_analysis['skills'],
            "skill_categories": resume_analysis['categories'],
            "experience_info": resume_analysis['experience'],
            "total_skills_count": resume_analysis['total_skills'],
            "top_categories": resume_analysis['top_categories']
        }
        
        # If job description is provided, calculate match
        if job_description.strip():
            match_result = job_matcher.calculate_match_score(resume_text, job_description)
            result.update({
                "job_match": match_result,
                "recommendations": match_result['recommendations']
            })
        
        return result
    except Exception as e:
        logger.error(f"Error in resume analysis: {e}")
        return {"error": str(e)}
def extract_text_from_pdf(pdf_file) -> str:
    """Extract text from PDF file."""
    try:
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        logger.error(f"Error extracting PDF text: {e}")
        return f"Error extracting text: {e}"

# API Routes
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint with network information."""
    import socket
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    return jsonify({
        "status": "healthy",
        "message": "Custom AI-Free Skill Matching API is running",
        "custom_ai_enabled": True,
        "pdf_processing_enabled": True,
        "version": "3.0.0-custom",
        "network_info": {
            "host": HOST,
            "port": PORT,
            "local_ip": local_ip,
            "hostname": hostname,
            "access_urls": [
                f"http://localhost:{PORT}",
                f"http://{local_ip}:{PORT}"
            ]
        },
        "cors_origins": cors_origins[:4]  # Show first 4 CORS origins
    })

@app.route('/api/match', methods=['POST'])
def match_resume():
    """Custom AI-free resume matching using rule-based algorithms."""
    try:
        # Validate input
        if 'resume' not in request.files or 'job_description' not in request.form:
            return jsonify({
                "error": "Missing resume file or job description"
            }), 400

        resume_file = request.files['resume']
        job_description_text = request.form['job_description']
        
        # Validate file type
        if not resume_file.filename.lower().endswith('.pdf'):
            return jsonify({
                "error": "Invalid file type",
                "details": "Please upload a PDF file"
            }), 400

        # Extract text from resume
        logger.info("Extracting text from resume...")
        resume_text = extract_text_from_pdf(resume_file.stream)
        
        if not resume_text:
            return jsonify({
                "error": "PDF processing failed",
                "details": "Could not extract text from PDF"
            }), 500

        # Use our custom AI-free analysis
        logger.info("Using custom AI-free skill matching...")
        
        # Process resume and job matching
        analysis_result = process_resume_analysis(resume_text, job_description_text)
        
        if "error" in analysis_result:
            return jsonify({
                "error": "Analysis failed",
                "details": analysis_result["error"]
            }), 500
        
        # Prepare comprehensive response
        response_data = {
            "overall_match_score": analysis_result.get("job_match", {}).get("overall_score", 0),
            "detailed_scores": analysis_result.get("job_match", {}).get("detailed_scores", {}),
            "matched_skills": analysis_result.get("job_match", {}).get("matched_skills", []),
            "missing_skills": analysis_result.get("job_match", {}).get("missing_skills", []),
            "extra_skills": analysis_result.get("job_match", {}).get("extra_skills", []),
            "skill_gaps": analysis_result.get("job_match", {}).get("skill_gaps", []),
            "recommendations": analysis_result.get("recommendations", []),
            "resume_analysis": {
                "total_skills": analysis_result.get("total_skills_count", 0),
                "skill_categories": analysis_result.get("skill_categories", {}),
                "experience_info": analysis_result.get("experience_info", {}),
                "top_categories": analysis_result.get("top_categories", [])
            },
            "processing_info": {
                "method": "custom_ai_free",
                "processing_time": "fast",
                "confidence": "high"
            }
        }
        
        logger.info(f"Analysis completed. Overall score: {response_data['overall_match_score']:.1f}%")
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error in match_resume: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "details": str(e)
        }), 500

@app.route('/api/analyze-skills', methods=['POST'])
def analyze_skills():
    """Dedicated endpoint for detailed skill analysis using custom AI-free system."""
    try:
        data = request.get_json()
        skills_text = data.get('text', '')
        analysis_type = data.get('type', 'comprehensive')  # basic, comprehensive, or comparison
        
        if not skills_text:
            return jsonify({"error": "No text provided for analysis"}), 400
        
        # Use our custom skill extractor
        analysis_result = skill_extractor.extract_skills_from_text(skills_text)
        
        return jsonify({
            "extracted_skills": list(analysis_result['skills'].keys()),
            "skill_details": analysis_result['skills'],
            "skill_count": analysis_result['total_skills'],
            "skill_categories": analysis_result['categories'],
            "experience_info": analysis_result['experience'],
            "top_categories": analysis_result['top_categories'],
            "analysis_type": analysis_type,
            "processing_method": "custom_ai_free"
        })
        
    except Exception as e:
        logger.error(f"Error in analyze_skills: {str(e)}")
        return jsonify({
            "error": "Skill analysis failed",
            "details": str(e)
        }), 500

# Helper function for skill categorization
def categorize_skills(skills: List[str]) -> Dict[str, List[str]]:
    """Categorize skills into different technology domains."""
    # Use our skill database for better categorization
    skill_db = skill_extractor.skill_db
    categories = {}
    
    for skill in skills:
        category = skill_db.find_skill_category(skill)
        if category not in categories:
            categories[category] = []
        categories[category].append(skill)
    
    return categories

@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    """Get skill recommendations based on current skills and target role."""
    try:
        data = request.get_json()
        current_skills = set(data.get('current_skills', []))
        target_skills = set(data.get('target_skills', []))
        job_category = data.get('job_category', 'general')
        
        # Generate learning path using our custom recommendation engine
        learning_path = recommendation_engine.generate_learning_path(current_skills, target_skills)
        
        return jsonify({
            "learning_path": learning_path,
            "job_category": job_category,
            "total_skills_to_learn": len(target_skills - current_skills),
            "processing_method": "custom_ai_free"
        })
        
    except Exception as e:
        logger.error(f"Error in get_recommendations: {str(e)}")
        return jsonify({
            "error": "Recommendation generation failed",
            "details": str(e)
        }), 500

@app.route('/api/learning-resources/<skill_name>', methods=['GET'])
def get_learning_resources(skill_name):
    """Get learning resources for a specific skill using custom recommendation engine."""
    try:
        # Generate learning path for this specific skill
        current_skills = set()  # Empty set - we want to learn this skill
        target_skills = {skill_name}
        
        learning_path = recommendation_engine.generate_learning_path(current_skills, target_skills)
        
        # Get specific resources for this skill
        resources = learning_path.get('learning_resources', {}).get(skill_name, [])
        timeline = learning_path.get('estimated_timeline', {}).get(skill_name, "1-2 months")
        dependencies = learning_path.get('skill_dependencies', {}).get(skill_name, [])
        
        return jsonify({
            "skill": skill_name,
            "learning_resources": resources,
            "estimated_timeline": timeline,
            "dependencies": dependencies,
            "priority": "high" if skill_name in learning_path.get('immediate_focus', []) else "medium",
            "processing_method": "custom_ai_free"
        })
        
    except Exception as e:
        logger.error(f"Error in get_learning_resources: {str(e)}")
        return jsonify({
            "error": "Learning resources retrieval failed",
            "details": str(e)
        }), 500

if __name__ == '__main__':
    import socket
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    print("=" * 60)
    print("🚀 CUSTOM AI-FREE SKILL MATCHING BACKEND")
    print("=" * 60)
    logger.info("Starting Custom AI-Free Skill Matching API...")
    logger.info("Using rule-based algorithms and fuzzy matching")
    print("🔧 No API keys required!")
    print("🤖 AI Features: Custom AI-Free System")
    print("📊 Processing: Rule-based + Fuzzy Matching")
    print(f"🌐 Server starting on: http://{HOST}:{PORT}")
    if HOST == '0.0.0.0':
        print(f"🌐 Local access: http://localhost:{PORT}")
    print(f"🌐 Network access: http://{local_ip}:{PORT}")
    print("📋 Available endpoints:")
    print("   • GET  /api/health")
    print("   • POST /api/match")
    print("   • POST /api/analyze-skills")
    print("   • POST /api/recommendations")
    print("   • GET  /api/learning-resources/<skill>")
    print("🔧 Configuration:")
    print(f"   • Max File Size: {app.config['MAX_CONTENT_LENGTH'] / (1024*1024):.0f}MB")
    print(f"   • Debug Mode: {DEBUG_MODE}")
    print(f"   • Environment: {FLASK_ENV}")
    print("=" * 60)
    
    app.run(host=HOST, port=PORT, debug=DEBUG_MODE)