# matching.py
# This module provides functions for matching skills and calculating similarity scores.

def semantic_similarity_score(skill1, skill2):
    """
    Computes semantic similarity between two skills using spaCy.
    Returns a float between 0 and 1.
    """
    import spacy
    nlp = spacy.load("en_core_web_sm")
    doc1 = nlp(skill1)
    doc2 = nlp(skill2)
    return doc1.similarity(doc2)

def overall_match_score(candidate_skills, job_skills):
    """
    Computes the overall match score between candidate and job skills.
    Uses average of best semantic similarity for each job skill.
    Returns a float between 0 and 1.
    """
    if not candidate_skills or not job_skills:
        return 0.0
    total_score = 0.0
    for job_skill in job_skills:
        best_score = max([semantic_similarity_score(job_skill, cand_skill) for cand_skill in candidate_skills])
        total_score += best_score
    return total_score / len(job_skills)

def match_skills(candidate_skills, job_skills):
    """
    Dummy implementation: Returns a list of matched skills.
    Replace with actual logic as needed.
    """
    return list(set(candidate_skills) & set(job_skills))
