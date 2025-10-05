from flask import Flask, request, jsonify
import spacy
from extraction import extract_text_and_layout, find_skill_section, extract_skills_from_text
from matching import semantic_similarity_score, overall_match_score, match_skills
from suggestions import suggest_skills_for_jd
from data import COMMON_SKILLS
import base64

app = Flask(__name__)

from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase_client import supabase
import spacy
import os
from extraction import extract_text_and_layout, find_skill_section, extract_skills_from_text
from matching import semantic_similarity_score, overall_match_score, match_skills
from suggestions import suggest_skills_for_jd
from data import COMMON_SKILLS
import base64

app = Flask(__name__)
CORS(app)



# Load spaCy model at startup
try:
    nlp = spacy.load("en_core_web_sm")
except Exception:
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# User registration/login (simple demo, not secure)
@app.route('/user', methods=['POST'])
def user_register_or_login():
    data = request.json
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')
    if not email or not username or not password:
        return jsonify({'error': 'Email, username, and password required'}), 400
    # Supabase: Upsert user (store password as plain text for demo; use hashing in production!)
    user_data = {'email': email, 'username': username, 'password': password}
    supabase.table('users').upsert(user_data).execute()
    return jsonify({'email': email, 'username': username})

# Skill analysis endpoint
@app.route('/analyze', methods=['POST'])
def analyze_skills():
    data = request.json
    resume_text = data.get('resume_text', '')
    jd_text = data.get('jd_text', '')
    email = data.get('email')
    if not resume_text or not jd_text or not email:
        return jsonify({'error': 'Missing required fields'}), 400
    # Extract skills
    resume_skills = extract_skills_from_text(resume_text, COMMON_SKILLS, top_n=100)
    jd_skills = extract_skills_from_text(jd_text, COMMON_SKILLS, top_n=100)
    resume_skill_names = set([s[0] if isinstance(s, (list, tuple)) else s for s in resume_skills])
    jd_skill_names = set([s[0] if isinstance(s, (list, tuple)) else s for s in jd_skills])
    matched_skills = list(resume_skill_names & jd_skill_names)
    missing_skills = list(jd_skill_names - resume_skill_names)
    extra_skills = list(resume_skill_names - jd_skill_names)
    recommendations = missing_skills
    score = round(100 * len(matched_skills) / max(len(jd_skill_names), 1))
    # Supabase: Insert analysis history
    history_data = {
        'email': email,
        'resume_skills': list(resume_skill_names),
        'jd_skills': list(jd_skill_names),
        'matched_skills': matched_skills,
        'missing_skills': missing_skills,
        'extra_skills': extra_skills,
        'recommendations': recommendations,
        'score': score
    }
    supabase.table('analysis_history').insert(history_data).execute()
    return jsonify({
        'matched_skills': matched_skills,
        'missing_skills': missing_skills,
        'extra_skills': extra_skills,
        'recommendations': recommendations,
        'score': score
    })

# Get user analysis history
@app.route('/history', methods=['GET'])
def get_history():
    email = request.args.get('email')
    if not email:
        return jsonify({'error': 'Email required'}), 400
    # Supabase: Fetch analysis history for user
    response = supabase.table('analysis_history').select('*').eq('email', email).execute()
    history = response.data if hasattr(response, 'data') else []
    return jsonify({'history': history})

@app.route("/extract_skills", methods=["POST"])
def api_extract_skills():
    data = request.json
    text = data.get("text", "")
    top_n = int(data.get("top_n", 30))
    skills = extract_skills_from_text(text, COMMON_SKILLS, top_n=top_n)
    return jsonify({"skills": skills})

@app.route("/match_skills", methods=["POST"])
def api_match_skills():
    data = request.json
    candidate_skills = data.get("candidate_skills", [])
    job_skills = data.get("job_skills", [])
    match = match_skills(candidate_skills, job_skills)
    score = overall_match_score(candidate_skills, job_skills)
    return jsonify({"matched_skills": match, "match_score": score})

@app.route("/suggest_skills", methods=["POST"])
def api_suggest_skills():
    data = request.json
    jd_text = data.get("jd_text", "")
    top_n = int(data.get("top_n", 10))
    suggestions = suggest_skills_for_jd(jd_text, COMMON_SKILLS, top_n=top_n)
    return jsonify({"suggested_skills": suggestions})

@app.route("/extract_resume_text", methods=["POST"])
def api_extract_resume_text():
    # Expects base64-encoded PDF bytes in 'pdf_base64'
    data = request.json
    pdf_base64 = data.get("pdf_base64", "")
    if not pdf_base64:
        return jsonify({"error": "Missing PDF data"}), 400
    pdf_bytes = base64.b64decode(pdf_base64)
    text, sections = extract_text_and_layout(pdf_bytes)
    skill_section = find_skill_section(sections)
    return jsonify({"text": text, "sections": sections, "skill_section": skill_section})

@app.route("/skills_list", methods=["GET"])
def api_skills_list():
    return jsonify({"skills": COMMON_SKILLS})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)