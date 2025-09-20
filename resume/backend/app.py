"""
Advanced Skill Matching Backend using LangGraph and LangChain
Provides intelligent skill matching between resumes and job descriptions
with AI-powered recommendations and insights.
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

# Configure logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables securely
try:
    from dotenv import load_dotenv
    # Load .env file from the same directory as this script
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        logger.info(f"✅ Loaded environment from: {env_path}")
    else:
        logger.warning(f"⚠️ No .env file found at: {env_path}")
        logger.warning("🔧 Run 'python setup_secure.py' to create one")
except ImportError:
    logger.warning("⚠️ python-dotenv not installed. Install with: pip install python-dotenv")

# Validate required environment variables
REQUIRED_ENV_VARS = ['LANGSMITH_API_KEY', 'OPENAI_API_KEY']
missing_vars = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]

if missing_vars:
    logger.error(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
    logger.error("🔧 Run 'python setup_secure.py' to configure them")
    exit(1)

# Define environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
LANGSMITH_API_KEY = os.getenv('LANGSMITH_API_KEY')
LANGSMITH_PROJECT = os.getenv('LANGSMITH_PROJECT', 'pr-unnatural-nudge-65')
LANGSMITH_TRACING = os.getenv('LANGSMITH_TRACING', 'true').lower() == 'true'

# Import LangChain components after environment validation
try:
    from langgraph.prebuilt import create_react_agent
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import HumanMessage, SystemMessage
    from langchain_core.tools import tool
    from langchain_core.prompts import ChatPromptTemplate
    import fitz  # PyMuPDF for PDF processing
    logger.info("✅ LangGraph and LangChain components imported successfully")
except ImportError as e:
    logger.error(f"❌ Error importing LangGraph/LangChain: {e}")
    logger.error("📦 Install with: pip install -U langgraph 'langchain[openai]'")
    exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configure CORS to allow frontend connections
CORS(app, origins=[
    "http://localhost:3000", 
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001"
], supports_credentials=True)

# Security configurations
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_FILE_SIZE_MB', 10)) * 1024 * 1024  # 10MB default
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
LANGSMITH_API_KEY = os.getenv('LANGSMITH_API_KEY')

# Initialize OpenAI LLM
if OPENAI_API_KEY != 'your-openai-api-key-here':
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        openai_api_key=OPENAI_API_KEY
    )
else:
    llm = None
    logger.warning("OpenAI API key not set. Some features will be limited.")

# Define tools for the agent
@tool
def extract_skills_from_text(text: str) -> List[str]:
    """Extract technical skills, programming languages, frameworks, and tools from text."""
    # Common technical skills database
    skills_database = [
        # Programming Languages
        "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust", "swift", "kotlin",
        "scala", "ruby", "php", "perl", "r", "matlab", "julia", "dart", "elixir", "clojure",
        
        # Web Technologies
        "html", "css", "react", "angular", "vue", "svelte", "next.js", "nuxt.js", "gatsby",
        "express", "fastapi", "django", "flask", "spring", "spring boot", "laravel", "rails",
        
        # Databases
        "mysql", "postgresql", "mongodb", "redis", "elasticsearch", "cassandra", "dynamodb",
        "sqlite", "oracle", "sql server", "neo4j", "influxdb", "couchdb",
        
        # Cloud Platforms
        "aws", "azure", "gcp", "google cloud", "heroku", "digitalocean", "vercel", "netlify",
        "cloudflare", "firebase", "supabase",
        
        # DevOps & Tools
        "docker", "kubernetes", "jenkins", "gitlab ci", "github actions", "terraform", "ansible",
        "chef", "puppet", "vagrant", "helm", "istio", "prometheus", "grafana", "elk stack",
        
        # Data Science & AI
        "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy", "jupyter", "apache spark",
        "hadoop", "kafka", "airflow", "mlflow", "kubeflow", "dask", "ray",
        
        # Mobile Development
        "android", "ios", "flutter", "react native", "xamarin", "ionic", "cordova",
        
        # Version Control & Collaboration
        "git", "github", "gitlab", "bitbucket", "svn", "mercurial",
        
        # Testing
        "jest", "pytest", "junit", "selenium", "cypress", "playwright", "postman", "insomnia",
        
        # Other Technologies
        "graphql", "rest api", "grpc", "websockets", "microservices", "serverless", "blockchain",
        "ethereum", "solidity", "web3", "oauth", "jwt", "ssl/tls"
    ]
    
    text_lower = text.lower()
    found_skills = []
    
    for skill in skills_database:
        if skill.lower() in text_lower:
            # Check for word boundaries to avoid partial matches
            import re
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.append(skill)
    
    return list(set(found_skills))  # Remove duplicates

@tool 
def calculate_skill_match_score(resume_skills: List[str], job_skills: List[str]) -> Dict[str, Any]:
    """Calculate detailed skill matching scores between resume and job requirements."""
    if not resume_skills or not job_skills:
        return {
            "overall_score": 0,
            "matched_skills": [],
            "missing_skills": job_skills,
            "additional_skills": resume_skills,
            "match_details": []
        }
    
    from rapidfuzz import fuzz
    
    matched_skills = []
    missing_skills = []
    match_details = []
    
    for job_skill in job_skills:
        best_match = None
        best_score = 0
        match_type = "missing"
        
        for resume_skill in resume_skills:
            # Exact match
            if job_skill.lower() == resume_skill.lower():
                best_match = resume_skill
                best_score = 100
                match_type = "exact"
                break
            
            # Fuzzy matching for similar skills
            similarity = fuzz.ratio(job_skill.lower(), resume_skill.lower())
            if similarity > best_score:
                best_score = similarity
                best_match = resume_skill
                
                if similarity >= 90:
                    match_type = "exact"
                elif similarity >= 70:
                    match_type = "similar"
                elif similarity >= 50:
                    match_type = "partial"
        
        match_detail = {
            "job_skill": job_skill,
            "matched_skill": best_match,
            "score": best_score,
            "match_type": match_type
        }
        
        if best_score >= 50:
            matched_skills.append(match_detail)
        else:
            missing_skills.append(job_skill)
            
        match_details.append(match_detail)
    
    # Calculate overall score
    overall_score = (len([m for m in match_details if m["score"] >= 50]) / len(job_skills)) * 100 if job_skills else 0
    
    # Find additional skills in resume not mentioned in job
    additional_skills = [skill for skill in resume_skills 
                        if not any(fuzz.ratio(skill.lower(), job_skill.lower()) >= 50 
                                 for job_skill in job_skills)]
    
    return {
        "overall_score": round(overall_score, 1),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "additional_skills": additional_skills,
        "match_details": match_details
    }

@tool
def generate_skill_recommendations(missing_skills: List[str], career_level: str = "mid") -> List[Dict[str, Any]]:
    """Generate learning recommendations for missing skills."""
    recommendations = []
    
    skill_categories = {
        "programming": ["python", "java", "javascript", "typescript", "go", "rust"],
        "web_development": ["react", "angular", "vue", "html", "css", "node.js"],
        "database": ["sql", "mysql", "postgresql", "mongodb", "redis"],
        "cloud": ["aws", "azure", "gcp", "docker", "kubernetes"],
        "data_science": ["pandas", "numpy", "tensorflow", "pytorch", "scikit-learn"],
        "devops": ["jenkins", "terraform", "ansible", "prometheus", "grafana"]
    }
    
    learning_resources = {
        "programming": {
            "beginner": ["Online tutorials", "Codecademy", "FreeCodeCamp"],
            "intermediate": ["LeetCode practice", "HackerRank challenges", "Personal projects"],
            "advanced": ["Open source contributions", "System design courses", "Architecture patterns"]
        },
        "web_development": {
            "beginner": ["MDN Web Docs", "Frontend Mentor", "Basic portfolio projects"],
            "intermediate": ["Full-stack applications", "State management", "API integration"],
            "advanced": ["Performance optimization", "Micro-frontends", "Advanced patterns"]
        },
        "cloud": {
            "beginner": ["AWS/Azure free tier", "Cloud practitioner certification", "Basic deployments"],
            "intermediate": ["Solutions architect certification", "Infrastructure as code", "CI/CD pipelines"],
            "advanced": ["Multi-cloud strategies", "Cost optimization", "Security best practices"]
        }
    }
    
    for skill in missing_skills[:8]:  # Limit to top 8 missing skills
        category = "general"
        for cat, skills in skill_categories.items():
            if any(skill.lower() in s.lower() or s.lower() in skill.lower() for s in skills):
                category = cat
                break
        
        priority = "high" if skill.lower() in ["python", "javascript", "sql", "aws", "docker"] else "medium"
        
        # Get appropriate learning resources
        resources = learning_resources.get(category, {
            "beginner": [f"Learn {skill} fundamentals", f"{skill} documentation"],
            "intermediate": [f"Build projects with {skill}", f"{skill} best practices"],
            "advanced": [f"Advanced {skill} concepts", f"{skill} architecture patterns"]
        })
        
        recommendation = {
            "skill": skill,
            "category": category,
            "priority": priority,
            "learning_path": {
                "beginner": resources.get("beginner", [f"Learn {skill} basics"]),
                "intermediate": resources.get("intermediate", [f"Practice {skill}"]),
                "advanced": resources.get("advanced", [f"Master {skill}"])
            },
            "estimated_time": "2-4 weeks" if priority == "high" else "1-2 weeks",
            "certification": f"{skill.title()} certification" if skill.lower() in ["aws", "azure", "gcp"] else None
        }
        
        recommendations.append(recommendation)
    
    return recommendations

# Utility functions
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

# Create the agent with tools
if llm:
    tools = [extract_skills_from_text, calculate_skill_match_score, generate_skill_recommendations]
    agent = create_react_agent(llm, tools)
else:
    agent = None

# API Routes
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "message": "Advanced Skill Matching API is running",
        "langsmith_enabled": bool(LANGSMITH_API_KEY),
        "openai_enabled": bool(llm),
        "version": "2.0.0"
    })

@app.route('/api/match', methods=['POST'])
def match_resume():
    """Advanced resume matching using LangGraph agent."""
    try:
        # Validate input
        if 'resume' not in request.files or 'job_description' not in request.form:
            return jsonify({
                "error": "Missing resume file or job description"
            }), 400

        resume_file = request.files['resume']
        job_description_text = request.form['job_description']
        use_ai_analysis = request.form.get('use_ai_analysis', 'true').lower() == 'true'
        
        # Validate file type
        if not resume_file.filename.lower().endswith('.pdf'):
            return jsonify({
                "error": "Invalid file type",
                "details": "Please upload a PDF file"
            }), 400

        # Extract text from resume
        logger.info("Extracting text from resume...")
        resume_text = extract_text_from_pdf(resume_file)
        
        if resume_text.startswith("Error"):
            return jsonify({
                "error": "PDF processing failed",
                "details": resume_text
            }), 500

        # Use agent for advanced analysis if available
        if agent and use_ai_analysis:
            logger.info("Using LangGraph agent for advanced skill matching...")
            
            # Create prompt for comprehensive analysis
            analysis_prompt = f"""
            Analyze this resume against the job description and provide comprehensive skill matching insights.
            
            RESUME TEXT:
            {resume_text[:3000]}  # Limit text length
            
            JOB DESCRIPTION:
            {job_description_text[:2000]}
            
            Please:
            1. Extract all technical skills from both the resume and job description
            2. Calculate detailed skill matching scores
            3. Generate personalized learning recommendations for missing skills
            4. Provide insights on the candidate's fit for this role
            
            Be thorough and provide actionable insights.
            """
            
            try:
                # Run the agent
                response = agent.invoke({
                    "messages": [HumanMessage(content=analysis_prompt)]
                })
                
                # Extract the final response
                agent_response = response["messages"][-1].content
                
                # Parse agent response (this would be more sophisticated in production)
                ai_insights = {
                    "analysis": agent_response,
                    "processed_by": "langgraph_agent",
                    "confidence": "high"
                }
                
            except Exception as e:
                logger.error(f"Agent analysis failed: {e}")
                ai_insights = {
                    "analysis": "AI analysis temporarily unavailable",
                    "processed_by": "fallback",
                    "confidence": "low"
                }
        else:
            ai_insights = None

        # Fallback to tool-based analysis
        logger.info("Performing tool-based skill analysis...")
        
        # Extract skills using tools
        resume_skills = extract_skills_from_text.invoke({"text": resume_text})
        job_skills = extract_skills_from_text.invoke({"text": job_description_text})
        
        # Calculate match scores
        match_results = calculate_skill_match_score.invoke({
            "resume_skills": resume_skills,
            "job_skills": job_skills
        })
        
        # Generate recommendations
        recommendations = generate_skill_recommendations.invoke({
            "missing_skills": match_results["missing_skills"],
            "career_level": "mid"  # Could be determined from resume
        })
        
        # Prepare comprehensive response
        response_data = {
            "overall_match_score": match_results["overall_score"],
            "skill_breakdown": {
                "total_job_skills": len(job_skills),
                "matched_skills": len(match_results["matched_skills"]),
                "missing_skills": len(match_results["missing_skills"]),
                "additional_skills": len(match_results["additional_skills"])
            },
            "detailed_matches": match_results["match_details"],
            "missing_skills": match_results["missing_skills"],
            "additional_skills": match_results["additional_skills"],
            "recommendations": recommendations,
            "ai_insights": ai_insights,
            "resume_skills": resume_skills,
            "job_skills": job_skills,
            "processing_info": {
                "used_langgraph": bool(agent and use_ai_analysis),
                "langsmith_tracing": bool(LANGSMITH_API_KEY),
                "model_used": "gpt-4o-mini" if llm else "rule-based",
                "processing_time": "real-time"
            }
        }
        
        logger.info(f"Analysis completed. Overall score: {match_results['overall_score']:.1f}%")
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error in match_resume: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "details": str(e)
        }), 500

@app.route('/api/analyze-skills', methods=['POST'])
def analyze_skills():
    """Dedicated endpoint for detailed skill analysis."""
    try:
        data = request.get_json()
        skills_text = data.get('text', '')
        analysis_type = data.get('type', 'comprehensive')  # basic, comprehensive, or comparison
        
        if not skills_text:
            return jsonify({"error": "No text provided for analysis"}), 400
        
        # Extract skills
        skills = extract_skills_from_text.invoke({"text": skills_text})
        
        # If agent is available, get detailed analysis
        detailed_analysis = None
        if agent:
            try:
                prompt = f"""
                Analyze these extracted skills and provide insights:
                Skills: {', '.join(skills)}
                Text: {skills_text[:1000]}
                
                Provide:
                1. Skill categorization (frontend, backend, database, cloud, etc.)
                2. Experience level assessment
                3. Technology stack coherence
                4. Market demand analysis
                5. Career progression suggestions
                """
                
                response = agent.invoke({
                    "messages": [HumanMessage(content=prompt)]
                })
                
                detailed_analysis = response["messages"][-1].content
                
            except Exception as e:
                logger.error(f"Detailed analysis failed: {e}")
        
        return jsonify({
            "extracted_skills": skills,
            "skill_count": len(skills),
            "detailed_analysis": detailed_analysis,
            "categories": categorize_skills(skills),
            "analysis_type": analysis_type
        })
        
    except Exception as e:
        logger.error(f"Error in analyze_skills: {str(e)}")
        return jsonify({
            "error": "Skill analysis failed",
            "details": str(e)
        }), 500

def categorize_skills(skills: List[str]) -> Dict[str, List[str]]:
    """Categorize skills into different technology domains."""
    categories = {
        "Programming Languages": [],
        "Web Development": [],
        "Database": [],
        "Cloud & DevOps": [],
        "Data Science & AI": [],
        "Mobile Development": [],
        "Other": []
    }
    
    category_mappings = {
        "Programming Languages": ["python", "java", "javascript", "typescript", "c++", "c#", "go", "rust"],
        "Web Development": ["react", "angular", "vue", "html", "css", "express", "django", "flask"],
        "Database": ["mysql", "postgresql", "mongodb", "redis", "sql"],
        "Cloud & DevOps": ["aws", "azure", "docker", "kubernetes", "jenkins", "terraform"],
        "Data Science & AI": ["tensorflow", "pytorch", "pandas", "numpy", "scikit-learn"],
        "Mobile Development": ["android", "ios", "flutter", "react native"]
    }
    
    for skill in skills:
        categorized = False
        for category, keywords in category_mappings.items():
            if any(keyword in skill.lower() for keyword in keywords):
                categories[category].append(skill)
                categorized = True
                break
        
        if not categorized:
            categories["Other"].append(skill)
    
    # Remove empty categories
    return {k: v for k, v in categories.items() if v}

if __name__ == '__main__':
    logger.info("Starting Advanced Skill Matching API with LangGraph...")
    logger.info(f"OpenAI enabled: {bool(llm)}")
    logger.info(f"LangSmith tracing: {bool(LANGSMITH_API_KEY)}")
    app.run(debug=True, host='0.0.0.0', port=5001)