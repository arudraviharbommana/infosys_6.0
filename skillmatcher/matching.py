# matching.py
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from rapidfuzz import process, fuzz


def semantic_similarity_score(text1, text2):
    """Computes TF-IDF cosine similarity between two texts (0-100)."""
    try:
        vect = TfidfVectorizer(stop_words="english").fit([text1, text2])
        tfidf = vect.transform([text1, text2])
        sim = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
        return float(sim * 100)
    except Exception:
        return 0.0


def overall_match_score(jd_skills, resume_skills, jd_text, resume_text, fuzz_threshold=60, qualification_factor=0.1):
    """
    Calculates the final match score by combining skill coverage and semantic similarity.
    Qualification factor is a new addition to boost the score.
    """
    if not jd_skills:
        return 0.0

    # Skill Coverage Score
    jd_count = len(jd_skills)
    matched_count = sum(1 for s in resume_skills if s[2] >= fuzz_threshold)
    skill_coverage = matched_count / jd_count if jd_count > 0 else 0.0

    # Semantic Similarity Score
    semantic = semantic_similarity_score(jd_text, resume_text) / 100.0

    # Add a factor for qualifications. This is a placeholder; you could
    # enhance this by checking for keywords like 'Master's', 'PhD', etc.
    # For now, let's assume a simple check for a 'qualification' section.
    # This is a simple, illustrative way to integrate this new requirement.
    qualification_bonus = 0
    if "education" in resume_text.lower() or "qualification" in resume_text.lower():
        qualification_bonus = qualification_factor

    # Weighted average: 70% skills, 20% semantic, 10% qualification bonus
    final = 0.7 * skill_coverage + 0.2 * semantic + qualification_bonus
    
    # Cap the score at 100
    return min(100.0, float(final * 100))


def match_skills(jd_skills_list, resume_skills, resume_text, fuzz_threshold=60):
    """
    Compares JD skills to resume skills and provides a detailed match summary.
    """
    matched = []
    resume_skill_names = [r[0] for r in resume_skills]
    for j in jd_skills_list:
        if j in resume_skill_names:
            r = next((x for x in resume_skills if x[0] == j), None)
            matched.append((j, r[1] if r else j, r[2] if r else 100))
        else:
            best = process.extractOne(j.lower(), resume_text.lower().split(), scorer=fuzz.partial_ratio)
            score = int(best[1]) if best else 0
            matched.append((j, best[0] if best else "", score))
            
    summary_rows = []
    for j, mtxt, sc in matched:
        status = "Matched" if sc >= fuzz_threshold else "Missing"
        summary_rows.append({"JD Skill": j, "Resume match": mtxt, "Score": sc, "Status": status})
        
    return summary_rows