def generate_summary(results):
    print("\n=== TOP CANDIDATE INSIGHTS ===\n")

    for r in results:
        print(f"{r['name']} → {r['score']} ({r['decision']})")
        print("Strengths:", ", ".join(r["strengths"]))
        print("Missing:", ", ".join(r["missing_skills"]))
        print("Reason:", r["explanation"])
        print("-" * 50)

from utils import call_ollama

def improve_jd(jd_text):

    prompt = f"""
You are a hiring expert.

Analyze this job description and suggest improvements.

JD:
{jd_text}

Return JSON:
{{
"missing_skills": [],
"unclear_requirements": [],
"suggestions": []
}}
"""

    return call_ollama("llama3:8b", prompt)

def detect_bias(jd_text):

    prompt = f"""
Detect hiring bias in this job description.

Check for:
- Gender bias
- Age bias
- Unnecessary requirements
- Over-restrictive criteria

JD:
{jd_text}

Return JSON:
{{
"bias_found": true/false,
"issues": [],
"suggestions": []
}}
"""

    return call_ollama("llama3:8b", prompt)