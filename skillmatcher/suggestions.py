# suggestions.py
# This module provides functions for suggesting skills for a job description.

def suggest_skills_for_jd(jd_text, common_skills=None, top_n=10):
    """
    Dummy implementation: Suggests skills for a job description by matching keywords.
    Replace with actual logic as needed.
    """
    if common_skills is None:
        common_skills = ["Python", "Machine Learning", "Data Analysis", "Communication", "Teamwork"]
    jd_text_lower = jd_text.lower()
    suggestions = [skill for skill in common_skills if skill.lower() in jd_text_lower]
    return suggestions[:top_n]
