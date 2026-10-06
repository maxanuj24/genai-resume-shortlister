import re
import os

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

from pdfminer.high_level import extract_text as pdfminer_extract_text
from docx import Document
from utils import call_ollama
from skill_utils import deduplicate, fallback_skills
from config import MODELS, RESUME_TEXT_LIMIT, RESUME_SECTIONS, EXCLUSION_PHRASES


# ---------------------------
# FILE READER
# ---------------------------
def read_file(path):
    try:
        if path.endswith(".pdf"):
            if fitz is not None:
                doc = fitz.open(path)
                text = "\n".join(page.get_text("text") for page in doc)
                doc.close()
                return text or pdfminer_extract_text(path)
            if PdfReader is not None:
                reader = PdfReader(path)
                text = "\n".join(page.extract_text() or "" for page in reader.pages)
                return text or pdfminer_extract_text(path)
            return pdfminer_extract_text(path)
        elif path.endswith(".docx"):
            return "\n".join([p.text for p in Document(path).paragraphs])
    except Exception:
        try:
            return pdfminer_extract_text(path)
        except Exception:
            return ""
    return ""


# ---------------------------
# TEXT CLEANING (CRITICAL)
# ---------------------------
def clean_text(text):
    # remove repeated merged names
    text = re.sub(r'(\b[A-Z]+\s?[A-Z]+\b)(\1)+', r'\1', text)

    # fix merged uppercase words (RONAKKUMAR → RONAK KUMAR)
    text = re.sub(r'([A-Z])([A-Z][a-z])', r'\1 \2', text)

    # normalize spaces
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


# ---------------------------
# FALLBACK NAME (SMART)
# ---------------------------
def fallback_name(text):
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    lines = [l for l in lines if "@" not in l]

    for line in lines[:15]:

        # ❌ skip job titles
        if any(x in line.lower() for x in ["engineer", "developer", "manager", "analyst"]):
            continue

        # ✅ ALL CAPS name
        if re.match(r'^[A-Z\s]{6,}$', line):
            words = line.split()
            if 2 <= len(words) <= 4:
                return " ".join(words[:2]).title()

        # ✅ Normal name
        if re.match(r'^[A-Z][a-z]+\s[A-Z][a-z]+', line):
            return line

    # 🔥 final fallback
    match = re.search(r'\b[A-Z]{4,}\s[A-Z]{4,}\b', text)
    if match:
        return match.group(0).title()

    return "Unknown"


# ---------------------------
# STRONG NAME EXTRACTOR
# ---------------------------
def normalize_name_candidate(name):
    if not isinstance(name, str):
        return ""
    name = name.strip()
    if not name:
        return ""
    # Remove noisy tokens like emails/links and titles
    name = re.sub(r"https?://\S+", " ", name)
    name = re.sub(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", " ", name, flags=re.I)
    name = re.sub(r"\s+", " ", name)
    return name


def filename_name(path):
    name = os.path.basename(path)
    name = os.path.splitext(name)[0]
    name = re.sub(r"[_-]+", " ", name)
    name = re.sub(r"(?i)resume|cv|dataengineer|data engineer|document|profile", " ", name)
    name = re.sub(r"\s+", " ", name).strip()
    if not name:
        return "Unknown"
    parts = [p for p in name.split() if p and not p.lower() in {"resume", "cv", "data", "engineer", "document"}]
    if len(parts) >= 2:
        return " ".join(parts[:2]).title()
    if len(parts) == 1:
        return parts[0].title()
    return "Unknown"


def extract_name_from_text(text):
    # Prefer names from the top of the resume, ignoring headers and titles.
    candidates = []
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    for line in lines[:25]:
        line = normalize_name_candidate(line)
        if not line:
            continue
        if any(token in line.lower() for token in ["contact", "summary", "skills", "experience", "education", "objective", "linkedin", "phone", "address", "email", "resume"]):
            continue
        if any(x in line.lower() for x in ["engineer", "developer", "manager", "analyst", "data engineer", "senior data"]):
            continue
        if len(line.split()) < 2:
            continue
        if re.match(r"^[A-Z][A-Za-z\s'-]{2,}$", line) or re.match(r"^[A-Z\s]{6,}$", line):
            candidates.append(line)

    for cand in candidates:
        cand = re.sub(r"\s+", " ", cand).strip()
        words = cand.split()
        if 2 <= len(words) <= 4:
            if re.match(r"^[A-Z\s]{6,}$", cand):
                # handles letter-spaced OCR names like "S H U B H A M K U M A R G U P T A"
                joined = re.sub(r"\s+", "", cand)
                if len(joined) >= 4:
                    return joined.title()
            return cand.title()

    match = re.search(r"\b[A-Z]{3,}\s+[A-Z]{3,}\b", text)
    if match:
        return match.group(0).title()

    return "Unknown"


# ---------------------------
# PARSE RESUME
# ---------------------------
def parse_resume(path):
    raw_text = read_file(path)
    text = clean_text(raw_text)[:RESUME_TEXT_LIMIT]

    prompt = f"""
You are a professional resume parser for any industry or job type.

PARSING RULES:
- Extract FULL NAME from top of resume (first 5 lines)
- Ignore/skip job titles and positions
- Never return single word as name
- Return clean human name (e.g., John Smith, Maria Garcia)
- Extract technical and soft skills (at least 3)
- Extract phone number if available (+country code or standard format)
- Extract years of experience / work history

Resume Content:
{text}

Return JSON Response:
{{
"name":"<full name of candidate>",
"phone":"<phone number with country code or empty>",
"skills":[<list of all skills found>],
"experience":[<list of previous roles/companies>],
"years_of_experience":<number>,
"education":[<list of educational background>]
}}

Return only valid JSON, no additional text.
"""

    data = call_ollama(MODELS["resume_parser"], prompt)

    if not isinstance(data, dict):
        data = {}

    # ---------------------------
    # NAME HANDLING
    # ---------------------------
    name = data.get("name")
    fallback_from_file = filename_name(path)

    if (
        not name
        or "@" in str(name)
        or len(str(name).split()) < 2
        or any(x in str(name).lower() for x in ["engineer", "developer", "manager", "analyst", "data engineer", "senior data", "contact", "skills", "summary", "education", "experience"])
    ):
        extracted = extract_name_from_text(text)
        if (
            extracted == "Unknown"
            or len(str(extracted).split()) < 2
            or any(x in str(extracted).lower() for x in ["engineer", "developer", "manager", "analyst", "data engineer", "senior data", "contact", "skills", "summary", "education", "experience"])
        ):
            name = fallback_from_file
        else:
            name = extracted

    # Final safety net: if the parse still produced a bad name, use the filename.
    if (
        not name
        or len(str(name).split()) < 2
        or any(x in str(name).lower() for x in ["engineer", "developer", "manager", "analyst", "data engineer", "senior data", "contact", "skills", "summary", "education", "experience"])
    ):
        name = fallback_from_file

    name = normalize_name_like_candidate(name)

    # ---------------------------
    # SKILLS HANDLING
    # ---------------------------
    skills = data.get("skills", []) or []
    # Always supplement LLM-extracted skills with simple fallback detection
    # from the resume text to capture explicit keywords the model may miss
    fb = fallback_skills(text)
    skills = list(set([s for s in skills if s] + [s for s in fb if s]))

    # ---------------------------
    # YEARS OF EXPERIENCE FALLBACK
    # If the LLM didn't extract years_of_experience, try simple regex
    # heuristics to infer years from the resume text.
    # ---------------------------
    years = data.get("years_of_experience", 0) or 0
    if not years:
        # look for explicit "X years" or "X yrs"
        m = re.search(r"(\d+)\s*\+?\s*(?:years|yrs)\b", text, re.I)
        if m:
            years = int(m.group(1))
        else:
            # look for date ranges like 2018-2022 and compute approximate years
            years_matches = re.findall(r"(20\d{2})\s*[-–—]\s*(20\d{2})", text)
            if years_matches:
                spans = [int(b) - int(a) for a, b in years_matches if int(b) >= int(a)]
                if spans:
                    years = max(spans)

    # ensure integer
    try:
        years = int(years)
    except Exception:
        years = 0

    # ---------------------------
    # PHONE NUMBER EXTRACTION
    # ---------------------------
    phone = data.get("phone", "") or ""
    if not phone:
        # Fallback: extract phone using regex patterns
        # Matches various phone formats across different countries
        phone_patterns = [
            r'\+\d{1,3}[\s\-\(\)]?\d{1,14}(?:[\s\-\(\)]?\d{1,4})*',  # International: +1-123-456-7890, +91 98765 43210
            r'(?:Phone|Tel|Mobile|Contact)[\s:\-]*\+?[\d\s\-\(\)\.]+',  # Labeled: Phone: +1 (123) 456-7890
            r'(?:^|\s)\d{10}\b',  # 10-digit US: 1234567890
            r'(?:\+\d{1,3})?[\s\-]?\(?[2-9]\d{2}\)?[\s\-]?[2-9]\d{2}[\s\-]?\d{4}',  # (123) 456-7890
        ]
        for pattern in phone_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                found_phone = match.group(0).strip()
                # Clean up the extracted phone
                if found_phone.lower().startswith(('phone', 'tel', 'mobile', 'contact')):
                    # Extract just the number part
                    parts = re.findall(r'[\d+\s\-()\.]', found_phone)
                    if parts:
                        phone = ''.join(parts).strip()
                        break
                else:
                    phone = found_phone
                    break

    return {
        "name": name,
        "phone": phone,
        "skills": deduplicate(skills),
        "experience": data.get("experience", []),
        "years_of_experience": years,
        "education": data.get("education", [])
    }


# ---------------------------
# PARSE JD
# ---------------------------
def parse_jd(text):
    """
    Parse job description to extract structured information.
    Works for any job type across any industry.
    """
    prompt = f"""
You are a job description parser. Extract structured information from the job post.

JOB DESCRIPTION:
{text}

Extract and return the following as JSON:
{{
"job_title": "<the actual job title>",
"company": "<company name if mentioned>",
"required_skills": [<list of must-have skills>],
"preferred_skills": [<list of nice-to-have skills>],
"experience": "<e.g., '3-5 years' or '5+ years' or '3-7 years'>",
"education": "<e.g., 'Bachelor in Computer Science' or 'High School'>",
"key_responsibilities": [<list of main duties>],
"job_type": "<full-time, part-time, contract, etc>",
"location": "<location or remote if mentioned>"
}}

Focus on extracting skills mentioned in the job description.
Return only valid JSON, no additional text.
"""
    data = call_ollama(MODELS["jd_parser"], prompt)
    if isinstance(data, dict) and (data.get("required_skills") or data.get("preferred_skills") or data.get("job_title")):
        return data

    raw = (text or "").replace("\r", "\n")
    jd = {
        "job_title": "",
        "company": "",
        "required_skills": [],
        "preferred_skills": [],
        "experience": "",
        "education": "",
        "key_responsibilities": [],
        "job_type": "",
        "location": ""
    }

    title_match = re.search(r"(?:role|position|job title)\s*[:\-]?\s*([^\n]+)", raw, re.I)
    if title_match:
        jd["job_title"] = title_match.group(1).strip()

    role_match = re.search(r"\bRole\s*:\s*([^\n]+)", raw, re.I)
    if role_match:
        jd["job_title"] = role_match.group(1).strip()

    experience_match = re.search(r"(?:experience required|experience|years of experience)\s*[:\-]?\s*([^\n]+)", raw, re.I)
    if experience_match:
        jd["experience"] = experience_match.group(1).strip()

    edu_match = re.search(r"(?:education)\s*[:\-]?\s*([^\n]+)", raw, re.I)
    if edu_match:
        jd["education"] = edu_match.group(1).strip()

    def extract_skill_list(section_name):
        m = re.search(rf"{re.escape(section_name)}\s*:?\s*\n?(.*?)(?=\n\s*(?:Preferred Skills|Experience Required|Experience|Education|Responsibilities|$))", raw, re.I | re.S)
        if not m:
            return []
        block = m.group(1)
        items = re.split(r"[,\n]+", block)
        cleaned = []
        for item in items:
            item = item.strip().strip("•-* ")
            if not item:
                continue
            cleaned.append(item)
        return cleaned

    jd["required_skills"] = extract_skill_list("Required Skills")
    jd["preferred_skills"] = extract_skill_list("Preferred Skills")

    if not jd["required_skills"]:
        for label in ["Must Have", "Must-Have", "Required", "Core Skills"]:
            jd["required_skills"] = extract_skill_list(label)
            if jd["required_skills"]:
                break

    if not jd["preferred_skills"]:
        for label in ["Nice to Have", "Nice-to-Have", "Preferred", "Good to Have"]:
            jd["preferred_skills"] = extract_skill_list(label)
            if jd["preferred_skills"]:
                break

    jd["key_responsibilities"] = []
    resp_match = re.search(r"(?:responsibilities|responsibility)\s*[:\-]?\s*\n?(.*?)(?=\n\s*(?:Education|Requirements|Skills|$))", raw, re.I | re.S)
    if resp_match:
        resp_text = resp_match.group(1)
        jd["key_responsibilities"] = [p.strip(" •-*\n") for p in re.split(r"[\n;]+", resp_text) if p.strip()]

    return jd

def normalize_name_like_candidate(cand):
    cand = re.sub(r"\s+", " ", str(cand)).strip()
    if not cand:
        return "Unknown"
    tokens = cand.split()

    # Remove exact duplicates caused by OCR noise.
    dedup = []
    for t in tokens:
        if dedup and t.lower() == dedup[-1].lower():
            continue
        dedup.append(t)
    tokens = dedup

    # Generic OCR corruption detection (language/country agnostic)
    # Strategy: Find merged/corrupted tokens that contain substrings of other tokens,
    # then extract the clean first name + cleanest surname candidate

    if len(tokens) >= 2:
        corrupted_indices = []
        # Find all potentially corrupted tokens
        for idx in range(1, len(tokens)):
            token_str = tokens[idx].lower()
            # Count how many other tokens are substrings of this one
            contained_count = sum(
                1 for i, t in enumerate(tokens)
                if i != idx and t.lower() in token_str and len(t) > 2
            )
            if contained_count > 0:
                corrupted_indices.append(idx)

        if corrupted_indices:
            # Found corrupted tokens - extract clean name
            if len(tokens) == 2 and 1 in corrupted_indices:
                # Two tokens: first is name, second is corrupted surname
                # Try to extract surname by removing first name
                first = tokens[0].lower()
                last = tokens[1].lower()
                clean = last.replace(first, "", 1).strip()
                if clean and len(clean) > 2:
                    tokens = [tokens[0], clean.title()]
            else:
                # Multiple tokens: use first name + first non-corrupted surname
                # or second token if it's the most obvious surname
                first_name = tokens[0]
                # Prefer the second token (likely the real surname) over others
                if len(tokens) > 1 and 1 not in corrupted_indices:
                    tokens = [first_name, tokens[1]]
                elif len(tokens) > 2:
                    # Find first non-corrupted surname candidate
                    for i in range(1, len(tokens)):
                        if i not in corrupted_indices:
                            tokens = [first_name, tokens[i]]
                            break
                    else:
                        # All are corrupted, use second as fallback
                        tokens = [first_name, tokens[1]]

    cand = " ".join(tokens)
    if len(cand.split()) > 4:
        cand = " ".join(cand.split()[:4])
    return cand.title()
