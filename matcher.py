import json
import re
import os
from utils import call_ollama
from config import (
    SKILL_SYNONYMS, SCORING_WEIGHTS, REQUIRED_SKILL_PENALTY_PER_SKILL,
    GENERIC_SKILLS, MIN_STRENGTHS, MIN_MISSING_SKILLS, MODELS
)


def normalize(val, max_val):
    try:
        val = float(val)
        # Support different scales returned by LLM or heuristics:
        # - 0..1 (probability-like) -> map to 0..max_val
        # - 0..10 (0-10 scale) -> map to 0..max_val
        # - >10 (already in points) -> cap at max_val
        if val <= 1:
            return int(val * max_val)
        if val <= 10:
            return int((val / 10) * max_val)
        return min(int(val), max_val)
    except Exception:
        return 0


def safe_list(val, fallback):
    return val if isinstance(val, list) and val else fallback


def merge_skill_lists(llm_list, fallback_list):
    """Merge two lists of skills/strings deterministically: canonicalize, dedupe and sort."""
    out = set()
    for v in (fallback_list or []):
        if isinstance(v, str) and v.strip():
            out.add(canonical_skill_name(v))
    for v in (llm_list or []):
        if isinstance(v, str) and v.strip():
            out.add(canonical_skill_name(v))
    # Remove empty strings
    out = {o for o in out if o}
    return sorted(out)


def merge_text_lists(llm_list, fallback_list):
    """Merge non-skill textual lists (strengths/weaknesses) deterministically."""
    out = []
    seen = set()
    for v in (fallback_list or []):
        if isinstance(v, str) and v.strip():
            t = v.strip()
            if t not in seen:
                seen.add(t)
                out.append(t)
    for v in (llm_list or []):
        if isinstance(v, str) and v.strip():
            t = v.strip()
            if t not in seen:
                seen.add(t)
                out.append(t)
    return out


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


def match_candidate(resume, jd, use_llm=True):
    # Step 1/2: normalize JD and resume skills (do this before any LLM call so we can feed
    # the deterministic lists into the prompt. This helps the model avoid hallucination
    # and only suggest additions.
    try:
        req_skills = [
            canonical_skill_name(s)
            for s in (jd.get("required_skills") or jd.get("skills") or [])
            if isinstance(s, str) and canonical_skill_name(s)
        ]
    except Exception:
        req_skills = []

    try:
        preferred_skills = [
            canonical_skill_name(s)
            for s in (jd.get("preferred_skills") or [])
            if isinstance(s, str) and canonical_skill_name(s)
        ]
    except Exception:
        preferred_skills = []

    try:
        resume_skills = [
            canonical_skill_name(s)
            for s in resume.get("skills", [])
            if isinstance(s, str) and canonical_skill_name(s)
        ]
    except Exception:
        resume_skills = []

    # make sets for deterministic matching
    resume_skill_set = set(resume_skills)
    required_skill_set = set(req_skills)
    preferred_skill_set = set(preferred_skills)

    # Step 3: exact skill match logic with synonym support (deterministic)
    matched_required = sorted({s for s in required_skill_set if skill_is_present_in_resume(s, resume_skill_set)})
    required_missing = sorted({s for s in required_skill_set if not skill_is_present_in_resume(s, resume_skill_set)})
    matched_preferred = sorted({s for s in preferred_skill_set if skill_is_present_in_resume(s, resume_skill_set)})
    preferred_missing = sorted({s for s in preferred_skill_set if not skill_is_present_in_resume(s, resume_skill_set)})

    mentioned = sorted(set(matched_required) | set(matched_preferred))
    matched = mentioned[:] if mentioned else sorted(resume_skill_set)
    experienced = mentioned[:] if mentioned else sorted(resume_skill_set)

    # Now optionally call the LLM with a prompt that includes these deterministic lists.
    # The prompt instructs the model to NOT remove or contradict the provided lists and to
    # only suggest additional missing skills or strengths/weaknesses. Ask for canonical
    # lowercase skill names and a confidence score so we can weigh suggestions.
    res = {}
    if use_llm and os.environ.get("DISABLE_LLM", "0") not in ("1", "true", "True"):
        prompt = f"""
You are a professional ATS evaluator. Use the deterministic lists provided below and DO NOT remove or contradict them.
Only suggest additional items if you are confident and explain why. Return JSON only with this structure:
{{
  "skills_score": <number>,
  "experience_score": <number>,
  "education_score": <number>,
  "fit_score": <number>,
  "matched_skills": [<lowercase canonical skills>],
  "missing_skills": [<lowercase canonical skills - only additional missing beyond deterministic lists>],
  "preferred_missing_skills": [<lowercase canonical skills - only additional preferred missing>],
  "strengths": [<text>],
  "weaknesses": [<text>],
  "explanation": "<assessment>",
  "confidence": <0-1 float optional>
}}

DETERMINISTIC LISTS (do not alter):
required_skills: {json.dumps(sorted(req_skills))}
preferred_skills: {json.dumps(sorted(preferred_skills))}
resume_skills: {json.dumps(sorted(resume_skills))}
matched_required: {json.dumps(sorted(matched_required))}
required_missing: {json.dumps(sorted(required_missing))}
preferred_missing: {json.dumps(sorted(preferred_missing))}

CANDIDATE RAW PROFILE:
{json.dumps(resume, sort_keys=True)}

JOB DESCRIPTION RAW:
{json.dumps(jd, sort_keys=True)}
"""
        try:
            res = call_ollama(MODELS["matcher"], prompt)
        except Exception:
            res = {}
    else:
        res = {}

    skills_score = normalize(res.get("skills_score", 0), SCORING_WEIGHTS["skills_score_max"])
    exp_score = normalize(res.get("experience_score", 0), SCORING_WEIGHTS["experience_score_max"])
    edu_score = normalize(res.get("education_score", 0), SCORING_WEIGHTS["education_score_max"])
    fit_score = normalize(res.get("fit_score", 0), SCORING_WEIGHTS["fit_score_max"])

    # Step 2: normalize JD and resume skills
    try:
        req_skills = [
            canonical_skill_name(s)
            for s in (jd.get("required_skills") or jd.get("skills") or [])
            if isinstance(s, str) and canonical_skill_name(s)
        ]
    except Exception:
        req_skills = []

    try:
        preferred_skills = [
            canonical_skill_name(s)
            for s in (jd.get("preferred_skills") or [])
            if isinstance(s, str) and canonical_skill_name(s)
        ]
    except Exception:
        preferred_skills = []

    try:
        resume_skills = [
            canonical_skill_name(s)
            for s in resume.get("skills", [])
            if isinstance(s, str) and canonical_skill_name(s)
        ]
    except Exception:
        resume_skills = []

    resume_skill_set = set(resume_skills)
    required_skill_set = set(req_skills)
    preferred_skill_set = set(preferred_skills)

    # Step 3: exact skill match logic with synonym support
    matched_required = sorted({s for s in required_skill_set if skill_is_present_in_resume(s, resume_skill_set)})
    required_missing = sorted({s for s in required_skill_set if not skill_is_present_in_resume(s, resume_skill_set)})
    matched_preferred = sorted({s for s in preferred_skill_set if skill_is_present_in_resume(s, resume_skill_set)})
    preferred_missing = sorted({s for s in preferred_skill_set if not skill_is_present_in_resume(s, resume_skill_set)})

    mentioned = sorted(set(matched_required) | set(matched_preferred))
    matched = mentioned if mentioned else sorted(resume_skill_set)
    experienced = mentioned if mentioned else sorted(resume_skill_set)

    # Step 4: score calculation
    if required_skill_set:
        coverage = len(matched_required) / len(required_skill_set)
    else:
        coverage = 1.0

    skills_score = max(skills_score, int(coverage * SCORING_WEIGHTS["skills_score_max"]))
    required_penalty = min(
        SCORING_WEIGHTS["skills_score_max"],
        len(required_missing) * REQUIRED_SKILL_PENALTY_PER_SKILL
    )

    def parse_exp_range(exp_str):
        if not exp_str or not isinstance(exp_str, str):
            return None, None
        m = re.search(r"(\d+)\s*[-–—]\s*(\d+)", exp_str)
        if m:
            return int(m.group(1)), int(m.group(2))
        m = re.search(r"(\d+)\s*\+", exp_str)
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
            exp_score = max(exp_score, 30)
        else:
            exp_score = max(exp_score, int((yrs / max(jd_exp_min, 1)) * 30))
    else:
        exp_score = max(exp_score, min(30, max(0, int(yrs) * 3)))

    final = max(0, skills_score + exp_score + edu_score + fit_score - required_penalty)
    if len(required_missing) >= 5:
        final = min(final, 49)

    # Step 5: strengths / weaknesses / missing skills derived from deterministic matching
    strengths = []
    if matched_required:
        strengths.append("Required skills present: " + ", ".join(matched_required[:3]))
    if matched_preferred:
        strengths.append("Preferred skills present: " + ", ".join(matched_preferred[:3]))
    if yrs:
        strengths.append(f"{yrs} years of experience")
    if not strengths:
        strengths = ["Relevant technical background"]

    weaknesses = []
    if required_missing:
        weaknesses.append("Missing required skills: " + ", ".join(required_missing[:3]))
    if preferred_missing:
        weaknesses.append("Missing preferred skills: " + ", ".join(preferred_missing[:3]))
    if not weaknesses:
        weaknesses = ["No major gaps identified"]

    if required_missing:
        missing_skills = required_missing
    elif preferred_missing:
        missing_skills = preferred_missing
    else:
        missing_skills = ["Not clearly defined"]

    preferred_missing_skills = preferred_missing if preferred_missing else []

    explanation = (
        f"Candidate matches {len(matched_required)} required skills and {len(matched_preferred)} preferred skills. "
        f"The profile has {yrs} years of experience and key gaps are {', '.join(missing_skills[:3]) if missing_skills else 'not clearly defined'}. "
        f"This is an overall {'strong fit' if final >= 60 else 'partial fit'} for the role."
    )

    # Step 6: merge with LLM output only when it adds extra value, but never overwrite concrete results
    if isinstance(res, dict):
        if res.get("matched_skills"):
            matched = safe_list(res.get("matched_skills"), matched)
        if res.get("missing_skills"):
            cleaned = [m for m in safe_list(res.get("missing_skills"), []) if isinstance(m, str) and m.strip()]
            if cleaned:
                missing_skills = cleaned
        if res.get("strengths"):
            cleaned = [s for s in safe_list(res.get("strengths"), []) if isinstance(s, str) and s.strip()]
            if cleaned:
                strengths = cleaned
        if res.get("weaknesses"):
            cleaned = [w for w in safe_list(res.get("weaknesses"), []) if isinstance(w, str) and w.strip()]
            if cleaned:
                weaknesses = cleaned
        if res.get("explanation"):
            explanation = res.get("explanation")

    # Final safety nets and canonicalization
    if not missing_skills or (missing_skills == ["Not clearly defined"] and (required_missing or preferred_missing)):
        missing_skills = required_missing or preferred_missing or ["Not clearly defined"]
    if not preferred_missing_skills and preferred_missing:
        preferred_missing_skills = preferred_missing
    if not matched:
        matched = mentioned if mentioned else sorted(resume_skill_set)

    # ensure all skill lists are canonical and sorted
    matched = sorted({canonical_skill_name(s) for s in matched if canonical_skill_name(s)})
    mentioned = sorted({canonical_skill_name(s) for s in mentioned if canonical_skill_name(s)})
    experienced = sorted({canonical_skill_name(s) for s in experienced if canonical_skill_name(s)})
    missing_skills = sorted({canonical_skill_name(s) for s in (missing_skills or []) if canonical_skill_name(s)}) if missing_skills and missing_skills != ["Not clearly defined"] else missing_skills
    preferred_missing_skills = sorted({canonical_skill_name(s) for s in (preferred_missing_skills or []) if canonical_skill_name(s)}) if preferred_missing_skills else []

    if not strengths:
        strengths = ["Relevant technical background"]
    if not weaknesses:
        weaknesses = ["No major gaps identified"]

    if final >= 80:
        decision = "Strong Hire"
    elif final >= 60:
        decision = "Consider"
    else:
        decision = "Reject"

    audit = {
        "raw_response": res,
        "cleaned_missing_skills": missing_skills,
        "parsed_resume_skills": resume.get("skills", []),
        "mentioned_skills": mentioned,
        "experienced_skills": experienced,
        "required_missing_count": len(required_missing),
        "required_penalty": required_penalty,
    }

    return {
        "final_score": int(final),
        "decision": decision,
        "strengths": strengths,
        "missing_skills": missing_skills,
        "mentioned_skills": mentioned,
        "experienced_skills": experienced,
        "preferred_missing_skills": preferred_missing_skills,
        "matched_skills": matched,
        "weaknesses": weaknesses,
        "explanation": explanation,
        "audit": audit,
    }

