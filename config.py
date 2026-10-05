"""
Configuration file for customizing the ATS matcher for different job roles.
This allows the system to work for any job type by adjusting parameters.
"""

# ===========================
# SKILL CATEGORIES (Generic)
# ===========================
# Extended skill list that covers multiple industries
# Dynamically expanded based on job description
GENERIC_SKILLS = [
    # Programming Languages
    "python", "java", "c++", "javascript", "typescript", "ruby", "go", "rust",
    "php", "swift", "kotlin", "scala", "r", "matlab", "groovy", "perl",

    # Data & Analytics
    "sql", "nosql", "mongodb", "cassandra", "elasticsearch", "redis",
    "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "keras",
    "spark", "pyspark", "hadoop", "airflow", "luigi", "dbt",
    "data modeling", "data warehousing", "etl", "elt", "eda",
    "tableau", "power bi", "looker", "grafana", "datadog",

    # Cloud & Infrastructure
    "aws", "gcp", "azure", "alibaba", "digitalocean", "heroku",
    "docker", "kubernetes", "terraform", "ansible", "jenkins",
    "ci/cd", "lambda", "ec2", "s3", "rds", "dynamodb",
    "bigquery", "redshift", "snowflake", "delta lake",

    # Databases
    "mysql", "postgresql", "oracle", "mariadb", "sqlite", "firestore",
    "dynamodb", "cosmosdb", "mongodb", "cassandra", "hbase",

    # Web & Frontend
    "html", "css", "react", "angular", "vue.js", "node.js", "express",
    "webpack", "gulp", "sass", "bootstrap", "jquery", "rest api",

    # DevOps & Infrastructure
    "linux", "windows", "docker", "kubernetes", "microservices",
    "api gateway", "load balancer", "monitoring", "logging",

    # Soft Skills
    "communication", "leadership", "teamwork", "project management",
    "problem solving", "critical thinking", "time management",
    "agile", "scrum", "kanban", "jira", "confluence",

    # Specialized Skills
    "machine learning", "deep learning", "nlp", "computer vision",
    "reinforcement learning", "transfer learning", "neural networks",
    "gis", "geospatial", "blockchain", "smart contracts",
    "devops", "sre", "platform engineering",
]

# ===========================
# SKILL SYNONYMS (Generic & Extensible)
# ===========================
# Maps variant names to canonical forms
# Can be extended with company-specific terminology
SKILL_SYNONYMS = {
    # Programming Languages
    "c#": "csharp",
    "c sharp": "csharp",
    "objective-c": "objectivec",
    "visual basic": "vb",

    # Data Tools
    "kubernets": "kubernetes",
    "k8s": "kubernetes",
    "data modeling": "data modeling",
    "data modelling": "data modeling",
    "pyspark": "pyspark",
    "py spark": "pyspark",
    "spark": "spark",
    "bigquery": "bigquery",
    "big query": "bigquery",
    "big-query": "bigquery",

    # Cloud Platforms
    "ms azure": "azure",
    "microsoft azure": "azure",
    "azures": "azure",
    "amazon web services": "aws",
    "google cloud": "gcp",
    "google cloud platform": "gcp",

    # Databases
    "postgres": "postgresql",
    "postgre": "postgresql",
    "mongo": "mongodb",

    # Frameworks & Tools
    "react": "react",
    "reactjs": "react",
    "react.js": "react",
    "angular": "angular",
    "angularjs": "angularjs",
    "vue": "vue.js",
    "vuejs": "vue.js",
    "node": "node.js",
    "nodejs": "node.js",
    "express": "express",
    "expressjs": "express",
}

# ===========================
# SCORING WEIGHTS (Customizable per role)
# ===========================
# Adjust these to prioritize different evaluation criteria
SCORING_WEIGHTS = {
    "skills_score_max": 40,        # Maximum points for skills
    "experience_score_max": 30,    # Maximum points for experience
    "education_score_max": 10,     # Maximum points for education
    "fit_score_max": 20,           # Maximum points for cultural/role fit
}

# Penalty for missing required skills (multiplied by number of missing skills)
REQUIRED_SKILL_PENALTY_PER_SKILL = 8

# ===========================
# EXTRACTION SETTINGS (Job-agnostic)
# ===========================
# Controls how the system extracts and interprets data

# Minimum characters for a skill name to be considered valid
MIN_SKILL_LENGTH = 2

# Maximum skills to extract (avoid noise)
MAX_SKILLS_TO_EXTRACT = 30

# Experience range parsing settings
EXPERIENCE_RANGE_PATTERN = r"(\d+)\s*-\s*(\d+)"  # Matches "5-7 years"
EXPERIENCE_PLUS_PATTERN = r"(\d+)\+"             # Matches "5+ years"
EXPERIENCE_SINGLE_PATTERN = r"(\d+)"             # Matches "5"

# ===========================
# LLM SETTINGS (Model-specific)
# ===========================
# Models to use for different tasks
MODELS = {
    "resume_parser": "llama3",      # For parsing resumes
    "jd_parser": "gemma:2b",        # For parsing job descriptions
    "matcher": "llama3:8b",         # For matching candidates
}

# ===========================
# RESUME PARSING SETTINGS (Generic)
# ===========================
# Top N characters to use for parsing (to keep LLM efficiency)
RESUME_TEXT_LIMIT = 6000

# Sections to look for in resumes (language/format independent)
RESUME_SECTIONS = [
    "skills", "experience", "education", "summary", "profile",
    "projects", "certifications", "languages", "technical",
    "work", "employment", "qualifications", "academic"
]

# ===========================
# PHRASE EXCLUSIONS (Generic noise removal)
# ===========================
# Words/phrases to exclude when extracting names or skills
EXCLUSION_PHRASES = {
    "names": [
        "engineer", "developer", "manager", "analyst", "consultant",
        "architect", "coordinator", "specialist", "officer", "executive",
        "data engineer", "senior data", "lead", "principal", "sr.",
        "jr.", "associate", "junior"
    ],
    "skills": [
        "working", "knowledge", "experience", "ability", "familiar",
        "skills", "proficiency", "expertise", "technical", "strong"
    ],
    "emails": [
        "@gmail", "@yahoo", "@hotmail", "@outlook"
    ]
}

# ===========================
# MATCHING STRATEGY (Tunable)
# ===========================
# How to interpret job descriptions and match skills

# Criteria for skill priority
SKILL_PRIORITY = {
    "required": 2.0,      # Weight for required skills
    "preferred": 1.0,     # Weight for preferred skills
    "nice_to_have": 0.5,  # Weight for nice-to-have skills
}

# Experience interpretation
MIN_EXPERIENCE_YEARS_FOR_SCORE = {
    "junior": 0,
    "mid": 2,
    "senior": 5,
    "lead": 8,
    "principal": 10,
}

# ===========================
# OUTPUT SETTINGS
# ===========================
# How to format and present results

# Minimum number of strengths to report
MIN_STRENGTHS = 2

# Minimum number of missing skills to report
MIN_MISSING_SKILLS = 1

# Formatting
RESULTS_CSV_COLUMNS = [
    "file", "name", "phone", "score", "decision",
    "strengths", "missing_skills", "matched_skills",
    "years_of_experience", "explanation"
]

# Decision thresholds
DECISION_THRESHOLDS = {
    "strong_accept": 85,
    "accept": 70,
    "maybe": 50,
    "reject": 0,
}

# ===========================
# HELPER FUNCTIONS
# ===========================

def get_decision_level(score):
    """Convert numeric score to decision level."""
    if score >= DECISION_THRESHOLDS["strong_accept"]:
        return "Strong Accept"
    elif score >= DECISION_THRESHOLDS["accept"]:
        return "Accept"
    elif score >= DECISION_THRESHOLDS["maybe"]:
        return "Maybe"
    else:
        return "Reject"


def extend_skill_list(additional_skills):
    """Extend the generic skill list with custom skills for a specific role."""
    global GENERIC_SKILLS
    GENERIC_SKILLS.extend(additional_skills)
    GENERIC_SKILLS = list(set(GENERIC_SKILLS))  # Remove duplicates


def extend_synonyms(additional_synonyms):
    """Extend the skill synonyms for role-specific terminology."""
    SKILL_SYNONYMS.update(additional_synonyms)

