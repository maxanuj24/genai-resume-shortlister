import json
import re
from utils import call_ollama
from config import (
    SKILL_SYNONYMS, SCORING_WEIGHTS, REQUIRED_SKILL_PENALTY_PER_SKILL,
    GENERIC_SKILLS, MIN_STRENGTHS, MIN_MISSING_SKILLS, MODELS
)


def normalize(val, max_val):
    try:
        val = float(val)
        if val <= 10:
            return int((val / 10) * max_val)
        return min(int(val), max_val)
    except:
        return 0


def safe_list(val, fallback):
    return val if isinstance(val, list) and val else fallback


def canonical_skill_name(skill):
    if not isinstance(skill, str):
        return ""
    s = skill.strip().lower()
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"[^a-z0-9+\s]", "", s)
    return s.strip()


def build_skill_set(values):
    out = set()
    for v in values or []:
        if not isinstance(v, str):
            continue
        c = canonical_skill_name(v)
        if c:
            out.add(c)
    return out


def normalize_skill_list(values):
    return sorted({canonical_skill_name(v) for v in values if canonical_skill_name(v)})

def skill_is_present_in_resume(skill, resume_skills):
    """Check if a required skill is present in resume (with synonym matching)."""
    target = canonical_skill_name(skill)
    if not target:
        return False
    if target in resume_skills:
        return True
    # Check synonyms from config
    canonical = SKILL_SYNONYMS.get(target, target)
    return canonical in resume_skills


def match_candidate(resume, jd):

    prompt = f"""
You are a professional ATS (Applicant Tracking System) evaluator.
Your task is to fairly and objectively evaluate a candidate against a job description.

EVALUATION CRITERIA:
- Skills Match: How many required/preferred skills does the candidate have?
- Experience: Is the candidate's experience level aligned with the role?
- Education: Does the candidate have relevant educational background?
- Overall Fit: Is this a good cultural/role match?

MANDATORY RESPONSE REQUIREMENTS:
- Provide at least {MIN_STRENGTHS} concrete strengths
- Identify at least {MIN_MISSING_SKILLS} areas for improvement
- Write a non-empty explanation for your assessment
- Be objective and fair

CANDIDATE PROFILE:
{json.dumps(resume)}

JOB DESCRIPTION:
{json.dumps(jd)}

SCORING BREAKDOWN:
- skills_score: 0-{SCORING_WEIGHTS['skills_score_max']} (Match between candidate skills and job requirements)
- experience_score: 0-{SCORING_WEIGHTS['experience_score_max']} (Experience level alignment)
- education_score: 0-{SCORING_WEIGHTS['education_score_max']} (Educational qualification relevance)
- fit_score: 0-{SCORING_WEIGHTS['fit_score_max']} (Overall role and cultural fit)

Return a JSON response with this exact structure:
{{
"skills_score": <number>,
"experience_score": <number>,
"education_score": <number>,
"fit_score": <number>,
"matched_skills": [<list of skills candidate has>],
"missing_skills": [<list of required skills candidate lacks>],
"strengths": [<list of candidate strengths>],
"weaknesses": [<list of candidate gaps>],
"explanation": "<detailed explanation of assessment>"
}}
"""

    res = call_ollama(MODELS["matcher"], prompt)

    skills = normalize(res.get("skills_score", 0), SCORING_WEIGHTS["skills_score_max"])
    exp = normalize(res.get("experience_score", 0), SCORING_WEIGHTS["experience_score_max"])
    edu = normalize(res.get("education_score", 0), SCORING_WEIGHTS["education_score_max"])
    fit = normalize(res.get("fit_score", 0), SCORING_WEIGHTS["fit_score_max"])

    try:
        req_skills = [s.lower() for s in (jd.get("required_skills") or jd.get("skills") or []) if isinstance(s, str)]
    except Exception:
        req_skills = []

    try:
        preferred_skills = [s.lower() for s in (jd.get("preferred_skills") or []) if isinstance(s, str)]
    except Exception:
        preferred_skills = []

    try:
        resume_skills = [s.lower() for s in resume.get("skills", []) if isinstance(s, str)]
    except Exception:
        resume_skills = []

    resume_skill_set = set(resume_skills)
    required_skill_set = set(req_skills)
    preferred_skill_set = set(preferred_skills)

    # HR-style scoring: required skills matter more than preferred ones.
    matched_required = required_skill_set & resume_skill_set
    required_missing = required_skill_set - resume_skill_set
    required_missing_count = len(required_missing)
    req_coverage = len(matched_required) / max(len(required_skill_set), 1)
    skills = max(skills, int(req_coverage * SCORING_WEIGHTS["skills_score_max"]))

    # Penalize candidates who miss multiple hard requirements.
    required_penalty = min(SCORING_WEIGHTS["skills_score_max"], required_missing_count * REQUIRED_SKILL_PENALTY_PER_SKILL)

    if req_skills:
        matched_count = len(required_skill_set & resume_skill_set)
        skill_score_det = int((matched_count / max(len(required_skill_set), 1)) * SCORING_WEIGHTS["skills_score_max"])
        skills = max(skills, skill_score_det)

    def parse_exp_range(exp_str):
        if not exp_str or not isinstance(exp_str, str):
            return None, None
        m = re.search(r"(\d+)\s*-\s*(\d+)", exp_str)
        if m:
            return int(m.group(1)), int(m.group(2))
        m = re.search(r"(\d+)\+", exp_str)
        if m:
            v = int(m.group(1))
            return v, v + 10
        m = re.search(r"(\d+)", exp_str)
        if m:
            v = int(m.group(1))
            return v, v
        return None, None

    jd_exp_min, jd_exp_max = parse_exp_range(jd.get("experience_required") or jd.get("experience") or "")
    yrs = resume.get("years_of_experience") or 0
    if jd_exp_min:
        if yrs >= jd_exp_min:
            exp_det = 30
        else:
            exp_det = int((yrs / max(jd_exp_min, 1)) * 30)
        exp = max(exp, exp_det)

    # Base score remains positive, but missing required skills now cut it down.
    final = max(0, skills + exp + edu + fit - required_penalty)

    # Hard reject rule for HR filtering: if too many critical gaps remain, reject regardless of raw model score.
    if required_missing_count >= 5:
        final = min(final, 49)

    matched = safe_list(res.get("matched_skills"), resume.get("skills", [])[:3])
    missing = safe_list(res.get("missing_skills"), ["Not clearly defined"])
    strengths = safe_list(res.get("strengths"), ["Relevant technical background"])
    weaknesses = safe_list(res.get("weaknesses"), ["Skill gaps exist"])

    explanation = res.get("explanation") or "Candidate partially matches job requirements."

    try:
        resume_skill_set = {canonical_skill_name(s) for s in resume.get("skills", []) if isinstance(s, str)}
        cleaned_missing = []
        for m in missing:
            if not isinstance(m, str):
                continue
            if skill_is_present_in_resume(m, resume_skill_set):
                continue
            cleaned_missing.append(m)
        missing = cleaned_missing if cleaned_missing else ["Not clearly defined"]
    except Exception:
        pass

    preferred_missing = []
    try:
        if preferred_skills:
            preferred_norm = {canonical_skill_name(p) for p in preferred_skills}
            for m in missing:
                if not isinstance(m, str):
                    continue
                if canonical_skill_name(m) in preferred_norm:
                    continue
                preferred_missing.append(m)
    except Exception:
        pass

    if preferred_missing:
        missing = preferred_missing

    mentioned = sorted(required_skill_set & resume_skill_set)
    mentioned += sorted(preferred_skill_set & resume_skill_set)
    mentioned = sorted(set(mentioned))
    experienced = sorted(set(normalize_skill_list(matched)))
    if not experienced:
        experienced = mentioned[:]

    audit = {
        "raw_response": res,
        "cleaned_missing_skills": missing,
        "parsed_resume_skills": resume.get("skills", []),
        "mentioned_skills": mentioned,
        "experienced_skills": experienced,
        "required_missing_count": required_missing_count,
        "required_penalty": required_penalty,
    }

    if final >= 80:
        decision = "Strong Hire"
    elif final >= 60:
        decision = "Consider"
    else:
        decision = "Reject"

    return {
        "final_score": int(final),
        "decision": decision,
        "strengths": strengths,
        "missing_skills": missing,
        "mentioned_skills": mentioned,
        "experienced_skills": experienced,
        "preferred_missing_skills": preferred_missing,
        "matched_skills": matched,
        "weaknesses": weaknesses,
        "explanation": explanation,
        "audit": audit
    }