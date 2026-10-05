import re
from config import GENERIC_SKILLS, MIN_SKILL_LENGTH, MAX_SKILLS_TO_EXTRACT


def normalize(skill):
    """Normalize skill name for comparison."""
    return re.sub(r"\s+", " ", str(skill).lower()).strip()


def deduplicate(skills):
    """Remove duplicate skills, preserving original case when possible."""
    seen = set()
    result = []
    for s in skills:
        normalized = normalize(s)
        if normalized and len(normalized) >= MIN_SKILL_LENGTH and normalized not in seen:
            seen.add(normalized)
            result.append(s)
    return result[:MAX_SKILLS_TO_EXTRACT]


def fallback_skills(text):
    """
    Extract skills from text by matching against known skill list.
    This is language/role agnostic - works for any job type.
    """
    if not text or not isinstance(text, str):
        return []

    t = text.lower()
    extracted = []

    for skill in GENERIC_SKILLS:
        skill_lower = skill.lower()
        # Check for exact skill match with word boundaries
        pattern = r'\b' + re.escape(skill_lower) + r'\b'
        if re.search(pattern, t):
            extracted.append(skill)

    # Also try to detect skill variations (e.g., "pyspark" within "py spark")
    for skill in GENERIC_SKILLS:
        skill_normalized = normalize(skill)
        if skill_normalized in t and skill not in extracted:
            extracted.append(skill)

    # Limit to avoid noise
    return extracted[:MAX_SKILLS_TO_EXTRACT]


