from flask import Flask, request, jsonify
import spacy
from extraction import extract_text_and_layout, find_skill_section, extract_skills_from_text
from matching import semantic_similarity_score, overall_match_score, match_skills
from suggestions import suggest_skills_for_jd
from data import COMMON_SKILLS
import base64

app = Flask(__name__)

# Load spaCy model at startup
try:
    nlp = spacy.load("en_core_web_sm")
except Exception:
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

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
    st.success("Resume processed successfully!")

    if show_layout:
        st.markdown("### 📝 Layout Analysis")
        st.info("Sample detected lines (top 40):")
        sample_lines = [s["text"] for s in sections[:40]]
        st.json(sample_lines)

    st.markdown("### 🎯 Detected 'Skills' Area")
    if skill_section_text:
        st.info(skill_section_text[:1000] + "...")
    else:
        st.warning("No explicit 'Skills' heading detected. Searching the entire resume text.")

    if not jd_text.strip():
        st.warning("Please paste JD text to enable skill matching.")
    else:
        # Extract skills from JD
        jd_candidates = extract_skills_from_text(jd_text, COMMON_SKILLS, top_n=100)
        jd_skills_list = [s[0] for s in jd_candidates]
        st.markdown("---")
        st.markdown("### 🔍 JD Skills (from vocabulary)")
        if not jd_skills_list:
            st.warning("No skills detected from the JD using the built-in vocabulary.")
        else:
            st.write(jd_skills_list)
        
        # Extract skills from Resume
        resume_search_text = skill_section_text if skill_section_text else resume_text
        res_found = extract_skills_from_text(resume_search_text, COMMON_SKILLS, top_n=200)
        res_filtered = [r for r in res_found if r[2] >= FUZZ_THRESHOLD]
        st.markdown("---")
        st.markdown("### ✨ Skills Found in Resume")
        if res_filtered:
            st.table([{"Skill": r[0], "Matched Text": r[1], "Score": r[2]} for r in res_filtered[:top_k]])
        else:
            st.write("No skills found above the threshold.")

        # Match and Score
        st.markdown("---")
        st.markdown("### ➡️ JD ↔ Resume Skill Match Summary")
        summary_rows = match_skills(jd_skills_list, res_found, resume_text, FUZZ_THRESHOLD)
        st.table(summary_rows)

        sem_score = semantic_similarity_score(jd_text, resume_text)
        overall_score = overall_match_score(jd_skills_list, res_found, jd_text, resume_text, FUZZ_THRESHOLD)

        st.markdown("---")
        st.markdown("## 📊 Overall Match Score")
        st.metric(label="Match Score", value=f"{overall_score:.1f}%")
        st.write(f"_(Semantic similarity: {sem_score:.2f}%)_")
        
        # Call the new function to get suggestions
        suggested_skills = suggest_skills_for_jd(jd_skills_list, res_found, FUZZ_THRESHOLD)

        st.markdown("### 💡 Suggestions")
        if suggested_skills:
            st.info("To improve your match score, consider adding these skills to your resume:")
            st.table({"Suggested Skills": suggested_skills})
            st.write("Tip: Even if you have minimal experience, listing these skills can significantly improve your match score and attract the recruiter's attention.")
        else:
            st.success("Your resume covers all the key skills detected in the JD. Excellent!")