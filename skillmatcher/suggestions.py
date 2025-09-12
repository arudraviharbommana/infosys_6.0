# suggestions.py
from rapidfuzz import process, fuzz

def suggest_skills_for_jd(jd_skills_list, resume_skills, fuzz_threshold=60, top_n=10):
    """
    Suggests skills from the JD that are missing from the resume based on a fuzzy match.
    
    Args:
        jd_skills_list (list): A list of skill strings from the Job Description.
        resume_skills (list): A list of tuples (skill, match_text, score) from the resume.
        fuzz_threshold (int): The minimum fuzzy match score to consider a skill as "found".
        top_n (int): The maximum number of skills to suggest.
        
    Returns:
        list: A list of suggested skill strings.
    """
    resume_skill_names = {r[0].lower() for r in resume_skills if r[2] >= fuzz_threshold}
    
    missing_skills = []
    for skill in jd_skills_list:
        if skill.lower() not in resume_skill_names:
            # Check for a weak fuzzy match to see if it's close but not strong enough
            best_match = process.extractOne(skill.lower(), list(resume_skill_names), scorer=fuzz.ratio)
            
            # If the best match score is below the threshold, it's truly "missing"
            if not best_match or best_match[1] < fuzz_threshold:
                missing_skills.append(skill)
                
    # Return the top N missing skills to keep the suggestions concise
    return missing_skills[:top_n]