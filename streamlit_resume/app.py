import streamlit as st
import pdfplumber
import re
import json
from io import BytesIO
from rapidfuzz import process, fuzz
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Try to load spaCy model; if not present, download it.
try:
    nlp = spacy.load("en_core_web_sm")
except Exception:
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")


# -------------------------
# Small skills vocabulary (extendable)
# -------------------------
COMMON_SKILLS = [
    "python", "java", "c++", "sql", "postgresql", "mysql", "mongodb",
    "machine learning", "deep learning", "nlp", "natural language processing",
    "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy", "data analysis",
    "aws", "azure", "docker", "kubernetes", "rest", "api", "javascript",
    "react", "node.js", "git", "linux", "communication", "problem solving",
    "computer vision", "opencv", "html", "css", "spark", "hadoop", "etl"
]

# -------------------------
# Helper functions
# -------------------------
def extract_text_and_layout(pdf_bytes):
    """
    Extract textual content and layout hints from PDF using pdfplumber.
    Returns combined_text, sections (list of dicts with text and bbox info)
    """
    sections = []
    full_text = []
    with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
        for pnum, page in enumerate(pdf.pages):
            # Get page-wide text
            page_text = page.extract_text() or ""
            full_text.append(page_text)

            # Layout analysis: identify blocks (top-down)
            try:
                blocks = page.extract_words(use_text_flow=True)
            except Exception:
                blocks = []
            # Group words into simple "lines" by y0 coordinate
            if blocks:
                cur_y = None
                cur_line = []
                for w in blocks:
                    y = round(w.get("top", 0))
                    txt = w.get("text", "")
                    if cur_y is None:
                        cur_y = y
                        cur_line = [txt]
                    elif abs(y - cur_y) <= 3:  # same line
                        cur_line.append(txt)
                    else:
                        line_text = " ".join(cur_line).strip()
                        if line_text:
                            sections.append({
                                "page": pnum + 1,
                                "text": line_text,
                                "y": cur_y
                            })
                        cur_y = y
                        cur_line = [txt]
                # last
                if cur_line:
                    line_text = " ".join(cur_line).strip()
                    sections.append({
                        "page": pnum + 1,
                        "text": line_text,
                        "y": cur_y
                    })

    combined = "\n".join([t for t in full_text if t])
    return combined, sections


def find_skill_section(sections):
    """
    Try to locate 'Skills' section lines from the layout sections list.
    Return text of nearby lines as a candidate skill-area string.
    """
    skill_lines = []
    for s in sections:
        txt = s["text"].lower()
        if re.search(r"\b(skill|skills|technical skills|expertise|technologies)\b", txt):
            # collect lines surrounding this line in the same page
            skill_lines.append(s)
    if not skill_lines:
        return None

    # Build nearby context (collect plus/minus N lines on same page)
    skill_texts = []
    for found in skill_lines:
        page = found["page"]
        y0 = found["y"]
        # choose lines on same page within y-distance
        nearby = [x["text"] for x in sections if x["page"] == page and abs(x["y"] - y0) <= 200]
        skill_texts.append("\n".join(nearby))
    # join all candidates
    return "\n".join(skill_texts)


def extract_skills_from_text(text, skills_vocab=COMMON_SKILLS, top_n=50, scorer=fuzz.token_sort_ratio):
    """
    Use a vocabulary and rapidfuzz to find best skill matches inside text.
    Returns list of (skill_from_vocab, best_match_in_text, score)
    """
    text_lower = text.lower()
    # For each skill candidate, check if exact substring exists quickly
    found = []
    for s in skills_vocab:
        s_lower = s.lower()
        if re.search(r"\b" + re.escape(s_lower) + r"\b", text_lower):
            found.append((s, s, 100))
        else:
            # fuzzy search: using process.extractOne on the text split into tokens/phrases
            # We'll do a simple sliding window over tokens (n-grams up to 4)
            tokens = re.findall(r"[a-zA-Z0-9\+\#\.\-]+", text_lower)
            candidates = []
            for n in range(1, 5):
                for i in range(len(tokens) - n + 1):
                    cand = " ".join(tokens[i:i+n])
                    candidates.append(cand)
            # use rapidfuzz process.extract to get best match for s_lower among candidates
            best = process.extractOne(s_lower, candidates, scorer=scorer, score_cutoff=50)
            if best:
                found.append((s, best[0], int(best[1])))
    # sort by score desc
    found_sorted = sorted(found, key=lambda x: x[2], reverse=True)
    # remove duplicates (keep highest)
    seen = set()
    filtered = []
    for a,b,c in found_sorted:
        if a not in seen:
            filtered.append((a,b,c))
            seen.add(a)
    return filtered[:top_n]


def semantic_similarity_score(text1, text2):
    """Compute TF-IDF cosine similarity (0-100)"""
    try:
        vect = TfidfVectorizer(stop_words="english").fit([text1, text2])
        tfidf = vect.transform([text1, text2])
        sim = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
        return float(sim * 100)
    except Exception:
        return 0.0


def overall_match_score(jd_skills, matched_skills, jd_text, resume_text):
    """
    Combine skill coverage score and semantic similarity into final score.
    jd_skills: list of extracted JD skills (strings)
    matched_skills: list of matched skills tuples (skill, matchtext, score)
    """
    if not jd_skills:
        return 0.0
    jd_count = len(jd_skills)
    matched_count = sum(1 for s in matched_skills if s[2] >= 60)  # threshold
    skill_coverage = matched_count / jd_count if jd_count > 0 else 0.0

    semantic = semantic_similarity_score(jd_text, resume_text) / 100.0

    # Weighted average: 70% skills, 30% semantic
    final = 0.7 * skill_coverage + 0.3 * semantic
    return float(final * 100)


# -------------------------
# Streamlit App UI
# -------------------------
st.set_page_config(page_title="AI SkillMatcher - Resume vs JD", layout="wide")
st.title("AI SkillMatcher — Resume ↔ Job Description Matching")
st.markdown("""
Upload a **Job Description** and a **Resume PDF**.  
The app will extract skills from the JD and resume, attempt layout analysis to find the skill section in the resume, and compute a match score.
""")

with st.sidebar:
    st.header("Settings")
    fuzz_threshold = st.slider("Fuzzy match threshold (min score for reported skills)", 40, 100, 60)
    top_k = st.number_input("Max matched skills to display", min_value=5, max_value=100, value=30)
    st.markdown("**(Extend `COMMON_SKILLS` in app.py to include domain-specific skills.)**")

col1, col2 = st.columns([2,3])

with col1:
    st.subheader("Job Description")
    jd_text = st.text_area("Paste Job Description here (or skills list)", height=240)
    if st.button("Auto-extract JD skills"):
        # Simple heuristic: look for lines with commas or bullets or 'skills' heading
        if not jd_text.strip():
            st.warning("Please paste a Job Description first.")
        else:
            # Extract candidate skills from JD by scanning for known skills
            jd_skills_found = extract_skills_from_text(jd_text, COMMON_SKILLS, top_n=100)
            jd_skills_list = [s[0] for s in jd_skills_found]
            st.success(f"Found {len(jd_skills_list)} skill candidates.")
            st.write(jd_skills_list)

with col2:
    st.subheader("Upload Resume (PDF)")
    uploaded_file = st.file_uploader("Upload resume PDF", type=["pdf"])
    show_layout = st.checkbox("Show layout analysis (detected lines)", value=True)

if uploaded_file:
    pdf_bytes = uploaded_file.read()
    # Extract text and layout
    with st.spinner("Extracting text and analyzing layout..."):
        resume_text, sections = extract_text_and_layout(pdf_bytes)
        skill_section_text = find_skill_section(sections)
    st.success("Resume processed.")

    st.markdown("### Layout Analysis")
    if show_layout:
        st.write("Sample detected lines (top 40):")
        # show first N lines detected
        sample_lines = [s["text"] for s in sections[:40]]
        st.write(sample_lines)

    st.markdown("### Detected 'Skills' area (heuristic)")
    if skill_section_text:
        st.info(skill_section_text[:1000])
    else:
        st.warning("No explicit 'Skills' heading detected by heuristic. We'll search entire resume text.")

    # If JD skills not provided, allow manual skills list
    if not jd_text.strip():
        st.warning("No Job Description provided. Please paste JD text or a comma-separated list of required skills.")
    else:
        # Extract skills from JD (vocab match)
        jd_candidates = extract_skills_from_text(jd_text, COMMON_SKILLS, top_n=100)
        jd_skills_list = [s[0] for s in jd_candidates]
        if not jd_skills_list:
            st.warning("No skills detected from the JD using the built-in vocabulary. Consider adding domain-specific skills to COMMON_SKILLS.")
        st.markdown("### JD candidate skills (from vocab)")
        st.write(jd_skills_list)

        # Extract skills from resume: prioritize skill_section_text if available, fallback to whole resume
        resume_search_text = skill_section_text if skill_section_text else resume_text
        res_found = extract_skills_from_text(resume_search_text, COMMON_SKILLS, top_n=200)
        # filter by threshold
        res_filtered = [r for r in res_found if r[2] >= fuzz_threshold]
        st.markdown("### Skills found in resume (vocab + fuzzy match)")
        if res_filtered:
            st.table([{"Skill": r[0], "Matched Text": r[1], "Score": r[2]} for r in res_filtered[:top_k]])
        else:
            st.write("No skills found above the threshold.")

        # Cross-match JD skills with resume detected skills (by vocab)
        matched = []
        resume_skill_names = [r[0] for r in res_found]
        for j in jd_skills_list:
            if j in resume_skill_names:
                # get corresponding resume match
                r = next((x for x in res_found if x[0] == j), None)
                matched.append((j, r[1] if r else j, r[2] if r else 100))
            else:
                # fuzzy check: see best fuzzy match between JD skill and resume_text tokens
                best = process.extractOne(j.lower(), resume_text.lower().split(), scorer=fuzz.partial_ratio)
                score = int(best[1]) if best else 0
                matched.append((j, best[0] if best else "", score))

        st.markdown("### JD → Resume skill match summary")
        summary_rows = []
        for j, mtxt, sc in matched:
            status = "Matched" if sc >= fuzz_threshold else "Missing"
            summary_rows.append({"JD Skill": j, "Resume match": mtxt, "Score": sc, "Status": status})
        st.table(summary_rows)

        # Semantic similarity between JD full text and resume full text
        sem = semantic_similarity_score(jd_text, resume_text)
        st.markdown("### Semantic similarity (TF-IDF)")
        st.write(f"Cosine similarity between JD and resume text: **{sem:.2f}%**")

        overall = overall_match_score(jd_skills_list, matched, jd_text, resume_text)
        st.markdown("## Overall Match Score")
        st.metric(label="Match Score", value=f"{overall:.1f}%")

        st.markdown("### Suggestions")
        # List missing JD skills
        missing = [r["JD Skill"] for r in summary_rows if r["Status"] == "Missing"]
        if missing:
            st.write(f"Missing or weakly matched skills: {missing[:20]}")
            st.write("Suggestions:")
            st.write("- Add these skills to your resume (if you have them) or acquire / highlight them.") 
            st.write("- For fresher resumes: apply to roles that require fewer of these skills or look for internships/trainings.")
        else:
            st.success("Good match — resume covers the JD skills detected.")

else:
    st.info("Upload a resume PDF to start. You can also paste the Job Description on the left.")

st.markdown("---")
st.caption("Prototype: uses simple heuristics + vocab + fuzzy matching + TF-IDF. For production: integrate a curated skills ontology, named-entity extraction trained for skills, and better layout/section parsing.")
