# Making the ATS Matcher Generic - Complete Guide

This document explains how to customize the ATS Resume Matcher for **any job type** across **any industry**.

## Architecture Overview

The system is now completely **job-role agnostic** and works through:

1. **Generic Configuration** (`config.py`) - Central place to customize everything
2. **Dynamic Skill Extraction** - Learns skills from both job description and resumes
3. **Flexible Scoring** - Adjustable weights for different evaluation criteria
4. **Extensible Skill Lists** - Works across all industries

---

## How to Use for Different Job Types

### Example 1: Data Engineer Role (Default)

The default configuration works for data engineering roles. No changes needed!

```bash
python main.py --jd_file job_description.txt --resume_folder resumes/
```

### Example 2: Software Engineer / Full Stack Developer

Create `config_softwareeng.py` or modify `config.py`:

```python
# In config.py, extend the skill list:
extend_skill_list([
    # Frontend
    "react", "vue", "angular", "svelte", "next.js", "nuxt",
    "tailwind", "material-ui", "bootstrap", "webpack",
    # Backend
    "nodejs", "express", "fastapi", "django", "spring boot",
    "microservices", "graphql", "rest api",
    # Testing
    "jest", "mocha", "pytest", "jasmine", "cypress",
    # Other Dev skills
    "git", "github", "gitlab", "bitbucket", "ci/cd",
])

# Adjust score weights based on role importance
SCORING_WEIGHTS = {
    "skills_score_max": 50,        # Skills more important for engineers
    "experience_score_max": 25,
    "education_score_max": 10,
    "fit_score_max": 15,
}
```

### Example 3: Product Manager Role

```python
# In config.py:
extend_skill_list([
    "product strategy", "market research", "user research",
    "roadmap planning", "stakeholder management", "oa",
    "competitive analysis", "pricing strategy",
    "metrics", "kpi", "analytics", "sql", "tableau",
    "agile", "scrum", "jira", "confluence",
    "figma", "wireframing", "prototyping",
])

# Adjust weights for PM role
SCORING_WEIGHTS = {
    "skills_score_max": 30,
    "experience_score_max": 40,    # Experience more important
    "education_score_max": 10,
    "fit_score_max": 20,
}

# Adjust experience expectations
MIN_EXPERIENCE_YEARS_FOR_SCORE = {
    "junior": 0,
    "mid": 3,
    "senior": 7,
    "lead": 10,
}
```

### Example 4: Sales Representative

```python
extend_skill_list([
    "sales", "negotiation", "client management", "crm",
    "salesforce", "hubspot", "pipedrive", "communication",
    "public speaking", "presentation", "cold calling",
    "lead generation", "deal closing", "customer retention",
])

# For sales, fit and communication are crucial
SCORING_WEIGHTS = {
    "skills_score_max": 25,
    "experience_score_max": 35,
    "education_score_max": 5,
    "fit_score_max": 35,           # High weight for soft skills fit
}
```

### Example 5: Marketing Manager

```python
extend_skill_list([
    "content marketing", "seo", "sem", "social media", "email marketing",
    "marketing automation", "hubspot", "marketo", "analytics",
    "google analytics", "a/b testing", "conversion optimization",
    "copywriting", "brand strategy", "campaign management",
    "market research", "competitive analysis", "budget planning",
])

SCORING_WEIGHTS = {
    "skills_score_max": 35,
    "experience_score_max": 30,
    "education_score_max": 10,
    "fit_score_max": 25,
}
```

### Example 6: DevOps Engineer

```python
extend_skill_list([
    "kubernetes", "docker", "terraform", "ansible", "jenkins",
    "gitlab-ci", "github-actions", "ci/cd", "infrastructure as code",
    "linux", "windows server", "networking", "monitoring",
    "prometheus", "grafana", "elk stack", "datadog",
    "deployment automation", "system administration", "aws", "gcp", "azure",
])

SCORING_WEIGHTS = {
    "skills_score_max": 45,        # Technical skills very important
    "experience_score_max": 30,
    "education_score_max": 5,
    "fit_score_max": 20,
}
```

---

## Step-by-Step Customization Guide

### Step 1: Identify Required Skills

Read through your job description and identify:
- Required technical skills
- Required soft skills
- Nice-to-have skills
- Industry-specific terminology

### Step 2: Add to Config

```python
# In config.py:

extend_skill_list([
    "skill1", "skill2", "skill name 1", "multi-word skill", ...
])

extend_synonyms({
    "variant1": "canonical_skill",
    "abbr": "full_skill_name",
    "alternate_name": "skill",
})
```

### Step 3: Adjust Scoring Weights

Based on your role, adjust what matters most:

```python
SCORING_WEIGHTS = {
    "skills_score_max": XX,        # 0-50
    "experience_score_max": XX,    # 0-50
    "education_score_max": XX,     # 0-20
    "fit_score_max": XX,           # 0-30
}
```

### Step 4: Set Experience Expectations

```python
MIN_EXPERIENCE_YEARS_FOR_SCORE = {
    "entry_level": 0,
    "junior": 1,
    "mid": 3,
    "senior": 7,
    "lead": 10,
}
```

### Step 5: Adjust Pass/Fail Thresholds

```python
DECISION_THRESHOLDS = {
    "strong_accept": 85,
    "accept": 70,
    "maybe": 50,
    "reject": 0,
}
```

### Step 6: Run the Matcher

```bash
python main.py \
    --resume_folder ./resumes \
    --jd_file ./job_description.txt \
    --top_k 10 \
    --output_file results.csv
```

---

## Key Configuration Options Explained

### 1. GENERIC_SKILLS
**What it does**: List of all skills the system recognizes.  
**When to change**: Add industry-specific skills or remove irrelevant ones.

```python
extend_skill_list(["pytorch", "tensorflow", "keras"])  # For ML roles
```

### 2. SKILL_SYNONYMS
**What it does**: Maps alternate names to canonical skill names.  
**When to change**: Add company-specific terminology or regional variations.

```python
extend_synonyms({
    "k8s": "kubernetes",
    "tf": "terraform",
    "iac": "infrastructure as code",
})
```

### 3. SCORING_WEIGHTS
**What it does**: Determines how important each evaluation criterion is.  
**When to change**: Different roles emphasize different aspects.

- `skills_score_max`: How much technical skills matter (0-50)
- `experience_score_max`: How much prior experience matters (0-50)
- `education_score_max`: How much formal education matters (0-20)
- `fit_score_max`: How much cultural/soft skills fit matters (0-30)

### 4. EXCLUSION_PHRASES
**What it does**: Filters out noise when parsing names and extracting data.  
**When to change**: If you're seeing false positives in extraction.

```python
EXCLUSION_PHRASES["names"].append("new_job_title_to_exclude")
```

### 5. DECISION_THRESHOLDS
**What it does**: Sets score ranges for Accept/Reject decisions.  
**When to change**: To be more/less strict in filtering.

```python
DECISION_THRESHOLDS = {
    "strong_accept": 90,   # More strict
    "accept": 75,
    "maybe": 50,
    "reject": 0,
}
```

---

## Advanced: Role-Specific Configuration Files

For large organizations, create separate config files per role:

```
configs/
  ├── config_data_engineer.py
  ├── config_full_stack.py
  ├── config_product_manager.py
  ├── config_devops.py
  └── config_sales.py
```

Usage:
```bash
# For data engineers
python main.py --config configs/config_data_engineer.py

# For full stack devs  
python main.py --config configs/config_full_stack.py
```

---

## How the System Works (Architecture)

### 1. Resume Parsing (`parser.py`)
- **Generic**: Extracts name, phone, skills, experience from any resume format
- **Customizable**: Uses skill lists from config to identify technical skills
- **AI-Enhanced**: Uses Ollama LLM for intelligent extraction

### 2. Job Description Parsing (`parser.py`)
- **Generic**: Extracts required/preferred skills and experience level
- **Dynamic**: Learns about required skills entirely from JD, not hardcoded

### 3. Skill Matching (`matcher.py`)
- **Generic**: Compares candidate skills against required skills
- **Configurable**: Weights for required vs preferred skills
- **Smart**: Uses synonym mapping for variant matching

### 4. Candidate Scoring (`matcher.py`)
- **Flexible**: All score max values are configurable
- **Holistic**: Considers skills, experience, education, and fit
- **Explainable**: LLM provides detailed reasoning

### 5. Results Export (`main.py`)
- **Consistent**: Always produces CSV with phone, name, skills, scores
- **Customizable**: Add/remove columns via config

---

## Industry Guidelines

### Tech Companies (Engineering-Heavy)
```python
SCORING_WEIGHTS = {"skills_score_max": 50, "experience_score_max": 30, ...}
REQUIRED_SKILL_PENALTY_PER_SKILL = 10  # Strict on required skills
```

### Consulting Firms
```python
SCORING_WEIGHTS = {"fit_score_max": 30, "experience_score_max": 35, ...}
MIN_EXPERIENCE_YEARS_FOR_SCORE["mid"] = 2  # Value speed
```

### Financial Services
```python
SCORING_WEIGHTS = {"education_score_max": 20, "experience_score_max": 40, ...}
DECISION_THRESHOLDS = {"strong_accept": 90, ...}  # Very strict
```

### Startups
```python
DECISION_THRESHOLDS = {"accept": 60, ...}  # More lenient, value potential
```

---

## Testing Your Customization

1. **Test with known candidates**
   ```bash
   python main.py --resume_folder test_resumes/ --jd_file senior_role.txt
   ```

2. **Verify skill extraction**
   - Check if all expected skills appear in matched_skills
   - Check if synonyms are working correctly

3. **Check scoring distribution**
   - Run same JD against different resumes
   - Verify scores make business sense

4. **Iterate**
   - Adjust weights based on results
   - Refine skill lists
   - Update thresholds

---

## Troubleshooting

### Issue: All candidates getting similar scores
**Solution**: Increase `REQUIRED_SKILL_PENALTY_PER_SKILL` or adjust weights to differentiate better

### Issue: Some skills not being extracted
**Solution**: Add them to `GENERIC_SKILLS` or create synonyms for variants

### Issue: Too many false positives in skill matching
**Solution**: Add longer, more specific skill names; increase `MIN_SKILL_LENGTH`

### Issue: Good candidates being rejected
**Solution**: Lower `DECISION_THRESHOLDS["accept"]` or reduce skill weights

---

## Summary

The ATS matcher is now **completely generic** and works for:
- ✅ Any industry (tech, finance, consulting, sales, marketing, etc.)
- ✅ Any role level (entry, mid, senior, lead)
- ✅ Any skill set (technical, soft skills, domain-specific)
- ✅ Any resume format (PDF, DOCX, TXT)
- ✅ Any evaluation criteria (via configurable weights)

Simply customize `config.py` for your specific role and industry!

