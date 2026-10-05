# ATS Resume Matcher - Generic & Extensible

A highly configurable Applicant Tracking System (ATS) that works for **any job type, any industry, any resume format**.

## Key Features

✅ **Completely Generic** - Works for tech, sales, finance, HR, marketing, operations, etc.  
✅ **Highly Configurable** - Adjust skills, weights, thresholds via `config.py`  
✅ **Multi-Format Resumes** - PDF, DOCX, TXT with robust OCR handling  
✅ **Intelligent Parsing** - Uses Ollama LLM for smart extraction  
✅ **Fair & Unbiased** - No hardcoded role assumptions  
✅ **Language Agnostic** - Name/phone extraction works globally  
✅ **Synonym Mapping** - Handles skill name variations  

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Update config.py for Your Role

```python
from config import extend_skill_list, extend_synonyms

# Add role-specific skills
extend_skill_list([
    "your", "specific", "skills", "here"
])

# Add skill synonyms
extend_synonyms({
    "variant_name": "canonical_name",
})

# Adjust scoring weights
SCORING_WEIGHTS = {
    "skills_score_max": 50,      # Emphasize skills
    "experience_score_max": 25,
    ...
}
```

### 3. Run the Matcher

```bash
python main.py \
    --resume_folder ./resumes \
    --jd_file ./job_description.txt \
    --top_k 10 \
    --output_file results.csv
```

---

## How It Works

### Architecture

```
User provides:
├── Job Description (job_description.txt)
└── Resumes (resumes/ folder)

Processing Pipeline:
├── 1. Parse JD
│   ├── Extract: required skills, preferred skills, experience level
│   ├── Parse: location, job type, company
│   └── Learn: what skills this role needs
│
├── 2. Parse Resumes
│   ├── Extract: name, phone, skills, experience, education
│   ├── Clean: OCR noise, normalize names
│   └── Enhance: fallback skill detection from generic list
│
├── 3. Match Candidates
│   ├── Compare: resume skills vs JD requirements
│   ├── Score: skills, experience, education, fit (weights from config)
│   ├── Penalize: missing required skills
│   └── Generate: detailed evaluation & explanation
│
└── Output: results.csv with rankings

Results CSV contains:
├── name, phone, file
├── score, decision (Accept/Reject/Maybe)
├── strengths, missing_skills, matched_skills
├── years_of_experience, explanation
└── ... customizable fields
```

---

## Configuration Guide

### config.py - The Control Center

All customization happens in `config.py`:

```python
# 1. Add/Remove Skills
GENERIC_SKILLS = [...]                    # Base skill list
extend_skill_list([...])                  # Add more skills

# 2. Skill Synonyms
SKILL_SYNONYMS = {...}                    # Handle variants
extend_synonyms({...})                    # Add more synonyms

# 3. Scoring Weights
SCORING_WEIGHTS = {
    "skills_score_max": 40,               # 0-50
    "experience_score_max": 30,           # 0-50
    "education_score_max": 10,            # 0-20
    "fit_score_max": 20,                  # 0-30
}

# 4. Pass/Fail Thresholds
DECISION_THRESHOLDS = {
    "strong_accept": 85,
    "accept": 70,
    "maybe": 50,
    "reject": 0,
}

# 5. LLM Models
MODELS = {
    "resume_parser": "llama3",
    "jd_parser": "gemma:2b",
    "matcher": "llama3:8b",
}
```

### Example Configurations

See `role_configs.py` for ready-to-use configurations:
- Frontend Developer
- Backend Developer  
- Data Scientist
- Data Engineer
- DevOps Engineer
- Product Manager
- Sales Engineer
- Marketing Manager

### Quick Examples

**For Frontend Dev Role:**
```python
from role_configs import FRONTEND_DEV_CONFIG
extend_skill_list(FRONTEND_DEV_CONFIG["skills_to_add"])
SCORING_WEIGHTS.update(FRONTEND_DEV_CONFIG["weights"])
```

**For Product Manager:**
```python
from role_configs import PRODUCT_MANAGER_CONFIG
extend_skill_list(PRODUCT_MANAGER_CONFIG["skills_to_add"])
SCORING_WEIGHTS.update(PRODUCT_MANAGER_CONFIG["weights"])
```

---

## Files & Structure

```
.
├── config.py                  # Configuration (customize here!)
├── role_configs.py            # Pre-built role configurations
├── parser.py                  # Resume & JD parsing
├── matcher.py                 # Candidate matching & scoring
├── skill_utils.py             # Skill extraction utilities
├── main.py                    # Entry point
├── utils.py                   # Helper functions
│
├── job_description.txt        # Your job description
├── resumes/                   # Resume files (PDF, DOCX, TXT)
└── results.csv                # Output file

Documentation:
├── README.md                  # This file
├── GENERALIZATION_GUIDE.md    # Detailed customization guide
└── requirements.txt           # Python dependencies
```

---

## Advanced Usage

### 1. Multiple Roles / Departments

Create separate configs:
```
configs/
  ├── config_engineering.py
  ├── config_sales.py
  └── config_operations.py
```

Run for each role:
```bash
# Engineering positions
python main.py --config configs/config_engineering.py

# Sales positions  
python main.py --config configs/config_sales.py
```

### 2. Dynamic Skill Extraction

The system automatically detects skills from job descriptions:
- Extracts required skills
- Extracts preferred skills
- Learns what this role needs across job postings

### 3. Custom Scoring Logic

Modify `DECISION_THRESHOLDS` per department:
```python
# Tech (strict)
DECISION_THRESHOLDS = {"strong_accept": 90, "accept": 80}

# Sales (lenient)
DECISION_THRESHOLDS = {"strong_accept": 75, "accept": 60}
```

### 4. Industry-Specific Tuning

```python
# Financial Services - Compliance Heavy
SCORING_WEIGHTS["education_score_max"] = 25  # Education matters more
REQUIRED_SKILL_PENALTY_PER_SKILL = 15        # Strict on requirements

# Startup - Potential Matters
DECISION_THRESHOLDS["accept"] = 60           # More lenient
```

---

## Customization Checklist

When adapting for a new role:

- [ ] Read the job description carefully
- [ ] List all technical skills mentioned
- [ ] List all soft skills mentioned
- [ ] Add them to `GENERIC_SKILLS` via `extend_skill_list()`
- [ ] Add any skill name variants to `SKILL_SYNONYMS`
- [ ] Adjust `SCORING_WEIGHTS` based on role importance
- [ ] Set `DECISION_THRESHOLDS` for your acceptance criteria
- [ ] Test with 5-10 known candidates
- [ ] Iterate based on results

---

## Examples

### Data Engineer JD
```plaintext
Requirements:
- Python, Spark, Hadoop, Airflow (required)
- AWS, GCP or Azure (required)
- SQL, ETL, Data Modeling (required)
- 3-7 years experience

Config:
SCORING_WEIGHTS = {
    "skills_score_max": 50,     ← Skills very important
    "experience_score_max": 25,
    "education_score_max": 10,
    "fit_score_max": 15,
}
```

### Product Manager JD
```plaintext
Requirements:
- Product Strategy, Roadmapping (required)
- User Research, Analytics (required)
- Communication, Leadership (preferred)
- 5+ years in product roles

Config:
SCORING_WEIGHTS = {
    "skills_score_max": 30,
    "experience_score_max": 40,  ← Experience critical
    "education_score_max": 10,
    "fit_score_max": 20,
}
```

### Sales Engineer JD
```plaintext
Requirements:
- Technical sales, solution design (required)
- Communication, Negotiation (required)
- Product knowledge, CRM (required)
- 3+ years selling technical products

Config:
SCORING_WEIGHTS = {
    "skills_score_max": 25,
    "experience_score_max": 30,
    "education_score_max": 10,
    "fit_score_max": 35,        ← Soft skills matter most
}
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Low scores across all candidates | Lower `DECISION_THRESHOLDS` or increase `skills_score_max` weight |
| High scores but wrong matches | Tighten `REQUIRED_SKILL_PENALTY_PER_SKILL` or add more required skills to JD |
| Skills not being recognized | Add to `GENERIC_SKILLS` or create synonyms in `SKILL_SYNONYMS` |
| Wrong candidate rankings | Adjust `SCORING_WEIGHTS` based on role priorities |
| Resume parsing errors | Update `EXCLUSION_PHRASES` or increase `RESUME_TEXT_LIMIT` |

---

## Performance Tips

1. **Faster Processing**: Reduce `RESUME_TEXT_LIMIT` (default 6000 chars)
2. **Better Accuracy**: Use `llama3:8b` instead of smaller models
3. **Batch Processing**: Process multiple JDs/resume folders in sequence
4. **Caching**: Results are cached in `cache.json` to avoid re-parsing

---

## Customization Limits

The system handles:
✅ All programming languages  
✅ All cloud platforms  
✅ All databases  
✅ Soft skills (communication, leadership, etc)  
✅ Industry-specific terminology  
✅ Regional variations  
✅ Multi-word skills  
❌ Purely credential-based matching (e.g., specific certifications)  
❌ Role-specific licenses (handled separately)  

---

## Support & Extensions

### Adding New Features

The modular architecture makes it easy to extend:

```python
# In matcher.py
def match_candidate(resume, jd):
    # ... existing code ...
    
    # Add custom scoring
    soft_skills_score = evaluate_soft_skills(resume, jd)
    
    # Add custom filtering
    if has_required_certifications(resume, jd):
        final_score += 10
    
    return result
```

### Debugging

Enable verbose output:
```python
# In utils.py
DEBUG = True  # Prints all LLM calls and parsing steps
```

Check audit logs:
```bash
ls audit_logs/  # See detailed evaluation for each candidate
```

---

## Contributing

To add new role configurations:
1. Create in `role_configs.py`
2. Test with sample resumes
3. Document in this README
4. Submit via PR

---

## License

[Your Organization]

---

## Questions?

Refer to:
- `GENERALIZATION_GUIDE.md` - Complete customization walkthrough
- `role_configs.py` - 8 pre-built industry examples
- `config.py` - Inline documentation for each setting

