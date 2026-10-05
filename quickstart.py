#!/usr/bin/env python3
"""
QUICK START EXAMPLES - Copy and paste these to use the ATS for different roles
"""

# ==================================================
# EXAMPLE 1: Frontend Developer Hiring
# ==================================================
def setup_frontend_dev_hiring():
    """Setup ATS for hiring Frontend Developers"""
    from config import extend_skill_list, SCORING_WEIGHTS

    # Add frontend-specific skills
    extend_skill_list([
        "react", "react.js", "vue", "vue.js", "angular",
        "html", "css", "sass", "typescript", "javascript",
        "webpack", "jest", "cypress", "tailwind", "bootstrap",
    ])

    # Adjust weights (skills matter more for engineers)
    SCORING_WEIGHTS["skills_score_max"] = 50
    SCORING_WEIGHTS["experience_score_max"] = 25

    print("✓ Frontend Developer hiring configured")


# ==================================================
# EXAMPLE 2: Data Science Hiring
# ==================================================
def setup_data_science_hiring():
    """Setup ATS for hiring Data Scientists"""
    from config import extend_skill_list, SCORING_WEIGHTS

    extend_skill_list([
        "python", "r", "sql", "machine learning",
        "tensorflow", "pytorch", "scikit-learn", "pandas",
        "statistics", "deep learning", "neural networks",
        "jupyter", "tableau", "git",
    ])

    # More balance - skills + education important
    SCORING_WEIGHTS["skills_score_max"] = 45
    SCORING_WEIGHTS["education_score_max"] = 20

    print("✓ Data Science hiring configured")


# ==================================================
# EXAMPLE 3: Sales Manager Hiring
# ==================================================
def setup_sales_manager_hiring():
    """Setup ATS for hiring Sales Managers"""
    from config import extend_skill_list, SCORING_WEIGHTS, DECISION_THRESHOLDS

    extend_skill_list([
        "sales", "negotiation", "leadership", "crm",
        "salesforce", "customer management", "team management",
        "strategic planning", "communication", "presentation",
    ])

    # Soft skills and experience matter most
    SCORING_WEIGHTS["skills_score_max"] = 25
    SCORING_WEIGHTS["experience_score_max"] = 40
    SCORING_WEIGHTS["fit_score_max"] = 25

    # Less strict threshold for sales (more on potential)
    DECISION_THRESHOLDS["accept"] = 65

    print("✓ Sales Manager hiring configured")


# ==================================================
# EXAMPLE 4: Backend Engineer Hiring
# ==================================================
def setup_backend_engineer_hiring():
    """Setup ATS for hiring Backend Engineers"""
    from config import extend_skill_list, SCORING_WEIGHTS

    extend_skill_list([
        "python", "java", "go", "node.js", "express",
        "django", "spring boot", "fastapi", "sql", "postgresql",
        "mongodb", "docker", "kubernetes", "aws", "gcp",
        "rest api", "graphql", "microservices", "ci/cd",
    ])

    # Heavy technical emphasis
    SCORING_WEIGHTS["skills_score_max"] = 55
    SCORING_WEIGHTS["experience_score_max"] = 20

    print("✓ Backend Engineer hiring configured")


# ==================================================
# EXAMPLE 5: Product Manager Hiring
# ==================================================
def setup_product_manager_hiring():
    """Setup ATS for hiring Product Managers"""
    from config import extend_skill_list, SCORING_WEIGHTS

    extend_skill_list([
        "product strategy", "roadmapping", "user research",
        "analytics", "a/b testing", "agile", "leadership",
        "communication", "stakeholder management", "sql",
        "figma", "jira", "data analysis",
    ])

    # Experience > skills for product roles
    SCORING_WEIGHTS["skills_score_max"] = 30
    SCORING_WEIGHTS["experience_score_max"] = 45

    print("✓ Product Manager hiring configured")


# ==================================================
# EXAMPLE 6: DevOps Engineer Hiring
# ==================================================
def setup_devops_engineer_hiring():
    """Setup ATS for hiring DevOps Engineers"""
    from config import extend_skill_list, SCORING_WEIGHTS

    extend_skill_list([
        "kubernetes", "docker", "terraform", "ansible",
        "ci/cd", "jenkins", "linux", "aws", "monitoring",
        "prometheus", "grafana", "terraform", "infrastructure",
    ])

    # Heavy technical requirements
    SCORING_WEIGHTS["skills_score_max"] = 55
    SCORING_WEIGHTS["experience_score_max"] = 30
    SCORING_WEIGHTS["education_score_max"] = 5

    print("✓ DevOps Engineer hiring configured")


# ==================================================
# EXAMPLE 7: HR Recruiter Hiring
# ==================================================
def setup_hr_recruiting_hiring():
    """Setup ATS for hiring HR Recruiters"""
    from config import extend_skill_list, SCORING_WEIGHTS

    extend_skill_list([
        "recruitment", "sourcing", "interviewing", "linkedin",
        "linkedin recruiting", "aats", "hr software", "workday",
        "communication", "relationship building", "time management",
        "candidate management", "job posting", "employer branding",
    ])

    # Balanced: skills + soft skills
    SCORING_WEIGHTS["skills_score_max"] = 35
    SCORING_WEIGHTS["fit_score_max"] = 35  # Soft skills important

    print("✓ HR Recruiter hiring configured")


# ==================================================
# EXAMPLE 8: Marketing Manager Hiring
# ==================================================
def setup_marketing_manager_hiring():
    """Setup ATS for hiring Marketing Managers"""
    from config import extend_skill_list, SCORING_WEIGHTS

    extend_skill_list([
        "marketing strategy", "content marketing", "seo", "sem",
        "social media", "email marketing", "google analytics",
        "a/b testing", "html", "css", "adobe creative suite",
        "campaign management", "budget planning", "leadership",
    ])

    # Mixed technical + creative
    SCORING_WEIGHTS["skills_score_max"] = 40
    SCORING_WEIGHTS["experience_score_max"] = 35

    print("✓ Marketing Manager hiring configured")


# ==================================================
# HOW TO USE
# ==================================================
"""
Method 1: Direct Python
In main.py or your script:

    from quickstart import setup_frontend_dev_hiring
    setup_frontend_dev_hiring()
    # ... proceed with main.py


Method 2: In config.py
Copy the extend_skill_list() and SCORING_WEIGHTS update into config.py

    # At the end of config.py:
    if __name__ == "__main__":
        # For Data Scientists:
        extend_skill_list([...])
        SCORING_WEIGHTS["skills_score_max"] = 45


Method 3: Create Role-Specific Script
    
    # save as run_frontend_hiring.py
    from quickstart import setup_frontend_dev_hiring
    from main import main
    
    setup_frontend_dev_hiring()
    main()
    
    # Run:
    python run_frontend_hiring.py --resume_folder resumes/ --jd_file job.txt


Command Line Examples
=====================

# Backend Engineer
python run_backend_hiring.py 

# Frontend Developer
python run_frontend_hiring.py

# Data Scientist
python run_data_science_hiring.py

# Product Manager
python run_pm_hiring.py

# Sales Manager
python run_sales_manager_hiring.py
"""


# ==================================================
# ADVANCED: Custom Role Setup
# ==================================================
def setup_custom_role(role_name, skills, weights, thresholds=None):
    """
    Generic function to setup ATS for any custom role

    Usage:
        setup_custom_role(
            "Solutions Architect",
            ["aws", "architecture", "design", "python", "java"],
            {"skills_score_max": 50, "experience_score_max": 30}
        )
    """
    from config import extend_skill_list, SCORING_WEIGHTS, DECISION_THRESHOLDS

    extend_skill_list(skills)
    SCORING_WEIGHTS.update(weights)
    if thresholds:
        DECISION_THRESHOLDS.update(thresholds)

    print(f"✓ {role_name} hiring configured")
    print(f"  Skills: {len(skills)} added")
    print(f"  Weights: {weights}")


# ==================================================
# ONE-LINER SETUPS
# ==================================================

"""
Quick copy-paste one-liners for each role:

Frontend Dev:
    python -c "from quickstart import setup_frontend_dev_hiring; setup_frontend_dev_hiring()" && python main.py

Backend Dev:
    python -c "from quickstart import setup_backend_engineer_hiring; setup_backend_engineer_hiring()" && python main.py

Data Scientist:
    python -c "from quickstart import setup_data_science_hiring; setup_data_science_hiring()" && python main.py

Product Manager:
    python -c "from quickstart import setup_product_manager_hiring; setup_product_manager_hiring()" && python main.py

Sales Manager:
    python -c "from quickstart import setup_sales_manager_hiring; setup_sales_manager_hiring()" && python main.py

DevOps Engineer:
    python -c "from quickstart import setup_devops_engineer_hiring; setup_devops_engineer_hiring()" && python main.py

HR Recruiter:
    python -c "from quickstart import setup_hr_recruiting_hiring; setup_hr_recruiting_hiring()" && python main.py

Marketing Manager:
    python -c "from quickstart import setup_marketing_manager_hiring; setup_marketing_manager_hiring()" && python main.py
"""


if __name__ == "__main__":
    # Demo: Show all available setups
    print("=" * 60)
    print("ATS QUICK START EXAMPLES - Available Configurations")
    print("=" * 60)
    print()

    print("1. Frontend Developer Hiring")
    print("2. Backend Engineer Hiring")
    print("3. Data Science Hiring")
    print("4. Sales Manager Hiring")
    print("5. Product Manager Hiring")
    print("6. DevOps Engineer Hiring")
    print("7. HR Recruiter Hiring")
    print("8. Marketing Manager Hiring")

    print()
    print("Usage Examples:")
    print("-" * 60)
    print()
    print("Option A - In Python:")
    print("  from quickstart import setup_frontend_dev_hiring")
    print("  setup_frontend_dev_hiring()")
    print("  from main import main")
    print("  main()")
    print()
    print("Option B - Direct Config Update:")
    print("  See examples within this file, copy to config.py")
    print()
    print("Option C - Custom Role:")
    print("  setup_custom_role('Your Role', ['skill1', 'skill2'], {...})")
    print()

