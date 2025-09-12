# app.py
import streamlit as st
import spacy

# Import functions from your modules
from extraction import extract_text_and_layout, find_skill_section, extract_skills_from_text
from matching import semantic_similarity_score, overall_match_score, match_skills
from suggestions import suggest_skills_for_jd
from data import COMMON_SKILLS

# Try to load spaCy model; if not present, download it.
try:
    nlp = spacy.load("en_core_web_sm")
except Exception:
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# Set a fixed fuzzy match threshold
FUZZ_THRESHOLD = 60

# -------------------------
# Streamlit App UI
# -------------------------
st.set_page_config(page_title="AI SkillMatcher - Resume vs JD", layout="wide")
st.title("🤖 AI SkillMatcher — Resume ↔ Job Description Matching")
st.markdown("""
Upload a **Job Description** and a **Resume PDF**. 
The app will extract skills, analyze text, and compute a match score.
""")

with st.sidebar:
    st.header("⚙️ Settings")
    top_k = st.number_input("Max skills to display", min_value=5, max_value=100, value=30)
    st.markdown("---")
    st.caption("Extend `COMMON_SKILLS` in `data.py` to add more skills.")

col1, col2 = st.columns([2, 3])

with col1:
    st.subheader("📋 Job Description")
    jd_text = st.text_area("Paste JD text here", height=240)
    if st.button("Auto-extract JD skills"):
        if not jd_text.strip():
            st.warning("Please paste a Job Description first.")
        else:
            jd_skills_found = extract_skills_from_text(jd_text, COMMON_SKILLS, top_n=100)
            jd_skills_list = [s[0] for s in jd_skills_found]
            st.success(f"Found {len(jd_skills_list)} skill candidates.")
            st.write(jd_skills_list)

with col2:
    st.subheader("📄 Upload Resume (PDF)")
    uploaded_file = st.file_uploader("Upload resume PDF", type=["pdf"])
    show_layout = st.checkbox("Show layout analysis", value=True)

if uploaded_file:
    pdf_bytes = uploaded_file.read()
    with st.spinner("Extracting text and analyzing layout..."):
        resume_text, sections = extract_text_and_layout(pdf_bytes)
        skill_section_text = find_skill_section(sections)
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