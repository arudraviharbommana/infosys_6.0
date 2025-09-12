# extraction.py
import pdfplumber
import re
from io import BytesIO
from rapidfuzz import process, fuzz
from data import COMMON_SKILLS


def extract_text_and_layout(pdf_bytes):
    """
    Extracts text and layout hints from a PDF using pdfplumber.
    Returns combined text and a list of sections with text and position info.
    """
    sections = []
    full_text = []
    with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
        for pnum, page in enumerate(pdf.pages):
            page_text = page.extract_text() or ""
            full_text.append(page_text)
            try:
                blocks = page.extract_words(use_text_flow=True)
            except Exception:
                blocks = []
            if blocks:
                cur_y = None
                cur_line = []
                for w in blocks:
                    y = round(w.get("top", 0))
                    txt = w.get("text", "")
                    if cur_y is None or abs(y - cur_y) <= 3:
                        cur_y = y
                        cur_line.append(txt)
                    else:
                        line_text = " ".join(cur_line).strip()
                        if line_text:
                            sections.append({"page": pnum + 1, "text": line_text, "y": cur_y})
                        cur_y = y
                        cur_line = [txt]
                if cur_line:
                    line_text = " ".join(cur_line).strip()
                    sections.append({"page": pnum + 1, "text": line_text, "y": cur_y})
    combined = "\n".join([t for t in full_text if t])
    return combined, sections


def find_skill_section(sections):
    """
    Tries to locate a 'Skills' section in the resume based on layout analysis.
    Returns the text of the found section or None.
    """
    skill_lines = []
    for s in sections:
        txt = s["text"].lower()
        if re.search(r"\b(skill|skills|technical skills|expertise|technologies)\b", txt):
            skill_lines.append(s)
    if not skill_lines:
        return None
    skill_texts = []
    for found in skill_lines:
        page = found["page"]
        y0 = found["y"]
        # Collect lines on the same page within a certain y-distance
        nearby = [x["text"] for x in sections if x["page"] == page and abs(x["y"] - y0) <= 200]
        skill_texts.append("\n".join(nearby))
    return "\n".join(skill_texts)


def extract_skills_from_text(text, skills_vocab=COMMON_SKILLS, top_n=50, scorer=fuzz.token_sort_ratio):
    """
    Uses a predefined vocabulary and fuzzy matching to find skills in text.
    Returns a list of tuples: (skill_from_vocab, best_match_in_text, score).
    """
    text_lower = text.lower()
    found = []
    for s in skills_vocab:
        s_lower = s.lower()
        if re.search(r"\b" + re.escape(s_lower) + r"\b", text_lower):
            found.append((s, s, 100))
        else:
            tokens = re.findall(r"[a-zA-Z0-9\+\#\.\-]+", text_lower)
            candidates = [" ".join(tokens[i:i+n]) for n in range(1, 5) for i in range(len(tokens) - n + 1)]
            best = process.extractOne(s_lower, candidates, scorer=scorer, score_cutoff=50)
            if best:
                found.append((s, best[0], int(best[1])))
    
    found_sorted = sorted(found, key=lambda x: x[2], reverse=True)
    seen = set()
    filtered = []
    for a, b, c in found_sorted:
        if a not in seen:
            filtered.append((a, b, c))
            seen.add(a)
    return filtered[:top_n]