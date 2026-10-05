"""
Ready-to-Use Configuration Examples for Different Job Roles
Copy these into config.py or create role-specific config files
"""

# ==================================================
# CONFIGURATION 1: Frontend Developer
# ==================================================
FRONTEND_DEV_CONFIG = {
    "skills_to_add": [
        "react", "react.js", "reactjs", "vue", "vue.js", "vuejs",
        "angular", "angularjs", "svelte", "ember",
        "html", "css", "sass", "scss", "less",
        "javascript", "typescript", "coffeescript",
        "webpack", "vite", "parcel", "gulp", "grunt",
        "npm", "yarn", "pnpm", "bower",
        "babel", "eslint", "prettier", "postcss",
        "tailwind", "bootstrap", "material-ui", "chakra",
        "jest", "mocha", "cypress", "playwright", "testing-library",
        "accessibility", "a11y", "seo", "performance",
        "responsive design", "mobile-first", "progressive enhancement",
    ],
    "weights": {
        "skills_score_max": 45,
        "experience_score_max": 25,
        "education_score_max": 10,
        "fit_score_max": 20,
    },
    "synonyms": {
        "js": "javascript",
        "ts": "typescript",
        "css-in-js": "css in js",
        "ui/ux": "design",
    }
}

# ==================================================
# CONFIGURATION 2: Backend Developer
# ==================================================
BACKEND_DEV_CONFIG = {
    "skills_to_add": [
        "python", "java", "go", "rust", "nodejs", "node.js", "express",
        "django", "fastapi", "spring boot", "spring", "flask",
        "sql", "nosql", "mongodb", "cassandra", "dynamodb",
        "postgresql", "mysql", "oracle", "redis", "elasticsearch",
        "rest api", "graphql", "grpc", "soap",
        "microservices", "monolithic architecture", "serverless",
        "docker", "kubernetes", "docker-compose",
        "git", "github", "gitlab", "bitbucket",
        "ci/cd", "jenkins", "gitlab-ci", "github-actions",
        "testing", "unit testing", "integration testing", "tdd",
        "api design", "database design", "system design",
        "authentication", "authorization", "security",
        "logging", "monitoring", "debugging", "performance optimization",
    ],
    "weights": {
        "skills_score_max": 50,
        "experience_score_max": 25,
        "education_score_max": 10,
        "fit_score_max": 15,
    },
    "synonyms": {
        "nodejs": "node.js",
        "api": "api",
        "oauth": "authentication",
        "mysql": "mysql",
        "nosql db": "nosql",
    }
}

# ==================================================
# CONFIGURATION 3: Data Scientist
# ==================================================
DATA_SCIENTIST_CONFIG = {
    "skills_to_add": [
        "python", "r", "sql", "scala",
        "pandas", "numpy", "scikit-learn", "scipy",
        "tensorflow", "pytorch", "keras", "mxnet",
        "machine learning", "deep learning", "nlp", "computer vision",
        "linear regression", "logistic regression", "random forest",
        "neural networks", "cnn", "rnn", "transformer",
        "statistical analysis", "hypothesis testing", "a/b testing",
        "data visualization", "matplotlib", "seaborn", "plotly",
        "jupyter notebook", "ipython", "git",
        "aws", "gcp", "azure", "sagemaker", "vertex ai",
        "mlflow", "kubeflow", "airflow", "spark",
        "tableau", "power bi", "looker",
        "data cleaning", "feature engineering", "model evaluation",
        "time series analysis", "nlp", "reinforcement learning",
        "experimental design", "statistical modeling",
    ],
    "weights": {
        "skills_score_max": 50,
        "experience_score_max": 20,
        "education_score_max": 20,
        "fit_score_max": 10,
    },
}

# ==================================================
# CONFIGURATION 4: Data Engineer
# ==================================================
DATA_ENGINEER_CONFIG = {
    "skills_to_add": [
        "python", "scala", "java", "sql",
        "spark", "pyspark", "hadoop", "hive",
        "kafka", "rabbitmq", "redis",
        "etl", "elt", "data pipeline", "data modeling",
        "airflow", "dbt", "luigi", "azkban",
        "postgresql", "mysql", "oracle", "dynamodb", "mongodb",
        "snowflake", "bigquery", "redshift", "delta lake",
        "aws", "gcp", "azure", "databricks",
        "docker", "kubernetes", "ci/cd",
        "git", "github", "gitlab",
        "data warehousing", "data lake", "lakehouse",
        "apache spark", "presto", "trino",
        "streaming", "real-time processing", "batch processing",
        "performance tuning", "query optimization",
    ],
    "weights": {
        "skills_score_max": 50,
        "experience_score_max": 25,
        "education_score_max": 10,
        "fit_score_max": 15,
    },
}

# ==================================================
# CONFIGURATION 5: DevOps Engineer
# ==================================================
DEVOPS_CONFIG = {
    "skills_to_add": [
        "docker", "kubernetes", "openshift", "docker-compose",
        "terraform", "ansible", "puppet", "chef", "cloudformation",
        "infrastructure as code", "iac", "ci/cd",
        "jenkins", "gitlab-ci", "github-actions", "circleci", "travis",
        "linux", "linux administration", "bash", "shell scripting",
        "networking", "tcp/ip", "dns", "ssl/tls",
        "aws", "gcp", "azure", "aws ec2", "aws s3", "aws rds",
        "container orchestration", "container registry", "docker registry",
        "monitoring", "logging", "observability",
        "prometheus", "grafana", "elk", "datadog", "newrelic",
        "git", "github", "gitlab", "version control",
        "security", "secret management", "vault",
        "kubernetes administration", "helm", "kops",
        "performance tuning", "capacity planning", "disaster recovery",
    ],
    "weights": {
        "skills_score_max": 50,
        "experience_score_max": 30,
        "education_score_max": 5,
        "fit_score_max": 15,
    },
}

# ==================================================
# CONFIGURATION 6: Product Manager
# ==================================================
PRODUCT_MANAGER_CONFIG = {
    "skills_to_add": [
        "product strategy", "product roadmap", "product vision",
        "user research", "market research", "competitive analysis",
        "user stories", "use cases", "requirements gathering",
        "agile", "scrum", "kanban", "sprint planning",
        "jira", "asana", "linear", "notion", "confluence",
        "analytics", "metrics", "kpi", "sql",
        "tableau", "power bi", "google analytics", "mixpanel",
        "a/b testing", "experimentation", "hypothesis testing",
        "prioritization", "roadmapping", "stakeholder management",
        "communication", "presentation", "storytelling",
        "figma", "sketch", "wireframing", "prototyping",
        "user interviews", "user testing", "usability testing",
        "api documentation", "technical literacy",
        "business acumen", "market sizing", "pricing strategy",
    ],
    "weights": {
        "skills_score_max": 30,
        "experience_score_max": 40,
        "education_score_max": 10,
        "fit_score_max": 20,
    },
    "experience_years": {
        "junior": 0,
        "mid": 3,
        "senior": 7,
        "lead": 10,
    }
}

# ==================================================
# CONFIGURATION 7: Sales Engineer
# ==================================================
SALES_ENGINEER_CONFIG = {
    "skills_to_add": [
        "technical sales", "presales", "solution architecture",
        "customer discovery", "needs analysis", "solution design",
        "presentation", "public speaking", "communication",
        "negotiation", "closing", "objection handling",
        "crm", "salesforce", "hubspot", "pipedrive",
        "product knowledge", "technical knowledge", "industry knowledge",
        "competitive analysis", "competitive positioning",
        "documentation", "proposal writing", "technical writing",
        "system design", "architecture", "best practices",
        "problem solving", "troubleshooting", "analytical thinking",
        "customer retention", "account management",
        "c-level communication", "stakeholder management",
    ],
    "weights": {
        "skills_score_max": 25,
        "experience_score_max": 35,
        "education_score_max": 10,
        "fit_score_max": 30,
    },
}

# ==================================================
# CONFIGURATION 8: Marketing Manager
# ==================================================
MARKETING_MANAGER_CONFIG = {
    "skills_to_add": [
        "content marketing", "content strategy", "copywriting",
        "seo", "sem", "ppc", "google ads", "facebook ads",
        "social media", "social media marketing", "social media management",
        "email marketing", "marketing automation", "hubspot", "marketo",
        "analytics", "google analytics", "mixpanel", "amplitude",
        "a/b testing", "conversion rate optimization", "cro",
        "brand strategy", "brand management", "brand positioning",
        "campaign management", "campaign planning", "campaign execution",
        "market research", "competitive analysis", "customer insights",
        "pricing strategy", "product positioning", "go-to-market",
        "communication", "presentation", "storytelling",
        "budget planning", "budget management", "roi analysis",
        "crm", "salesforce", "hubspot",
    ],
    "weights": {
        "skills_score_max": 35,
        "experience_score_max": 30,
        "education_score_max": 10,
        "fit_score_max": 25,
    },
}

# ==================================================
# HOW TO USE THESE CONFIGURATIONS
# ==================================================
"""
Option 1: Direct Usage
In config.py:
    config = FRONTEND_DEV_CONFIG
    extend_skill_list(config["skills_to_add"])
    SCORING_WEIGHTS.update(config["weights"])
    if "synonyms" in config:
        extend_synonyms(config["synonyms"])

Option 2: Create Role-Specific Files
Create frontend_config.py:
    from config import *
    config = FRONTEND_DEV_CONFIG
    extend_skill_list(config["skills_to_add"])
    ...

Then use:
    python main.py --config frontend_config.py

Option 3: Environment-Based
Use environment variables to select configuration:
    export JOB_ROLE="frontend_dev"
    python main.py  # Automatically loads FRONTEND_DEV_CONFIG
"""

