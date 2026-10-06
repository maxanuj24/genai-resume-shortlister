import os
import argparse
import pandas as pd
from parser import parse_resume, parse_jd
from matcher import match_candidate


def print_insights(results):
    print("\n=== TOP CANDIDATE INSIGHTS ===\n")

    for r in results:
        print(f"{r['name']} → {r['score']} ({r['decision']})")

        print("Strengths:")
        for s in r["strengths"]:
            print("  ✔", s)

        print("Missing:")
        for m in r["missing_skills"]:
            print("  ✘", m)

        print("Reason:", r["explanation"])
        print("-" * 50)


def main():
    parser = argparse.ArgumentParser(description="ATS Resume Matcher")

    parser.add_argument(
        "--resume_folder",
        default="./resumes",
        help="Path to resumes folder (default: ./resumes)"
    )
    parser.add_argument(
        "--jd_file",
        default="./job_description.txt",
        help="Path to job description file (default: ./job_description.txt)"
    )
    parser.add_argument(
        "--top_k",
        type=int,
        default=5,
        help="Top K candidates to retrieve (default: 5)"
    )
    parser.add_argument(
        "--openai_key",
        default=None,
        help="OpenAI API Key (optional)"
    )
    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="Disable LLM calls and use deterministic matching only"
    )
    parser.add_argument(
        "--ollama_temp",
        type=float,
        default=0.0,
        help="Temperature for Ollama LLM (default: 0.0)"
    )
    parser.add_argument(
        "--force-llm-refresh",
        action="store_true",
        help="Force refresh LLM responses by bypassing cache (useful to get fresh outputs)"
    )
    parser.add_argument(
        "--output_file",
        default="results.csv",
        help="Output CSV file path (default: results.csv)"
    )

    args = parser.parse_args()

    if args.openai_key:
        os.environ["OPENAI_API_KEY"] = args.openai_key

    # set ollama temperature and optionally disable LLM
    os.environ["OLLAMA_TEMPERATURE"] = str(args.ollama_temp)
    if args.no_llm:
        os.environ["DISABLE_LLM"] = "1"
    else:
        os.environ.pop("DISABLE_LLM", None)
    if args.force_llm_refresh:
        os.environ["FORCE_OLLAMA_REFRESH"] = "1"
    else:
        os.environ.pop("FORCE_OLLAMA_REFRESH", None)

    if not os.path.exists(args.jd_file):
        print(f"Error: Job description file not found at {args.jd_file}")
        return

    with open(args.jd_file, "r") as f:
        jd_text = f.read()
    jd = parse_jd(jd_text)

    results = []

    if not os.path.exists(args.resume_folder):
        print(f"Error: Resume folder not found at {args.resume_folder}")
        return

    for file in os.listdir(args.resume_folder):
        if file.endswith((".pdf", ".docx", ".txt")):
            path = os.path.join(args.resume_folder, file)
            resume = parse_resume(path)
            score = match_candidate(resume, jd, use_llm=(not args.no_llm))

            results.append({
                "file": file,
                "name": resume.get("name", file),
                "phone": resume.get("phone", ""),
                "score": score.get("final_score", 0),
                "decision": score.get("decision", "N/A"),
                "strengths": score.get("strengths", []),
                "missing_skills": score.get("missing_skills", []),
                "mentioned_skills": score.get("mentioned_skills", []),
                "experienced_skills": score.get("experienced_skills", []),
                "preferred_missing_skills": score.get("preferred_missing_skills", []),
                "explanation": score.get("explanation", ""),
                "audit": score.get("audit", {})
            })

    if not results:
        print("No resumes found in folder.")
        return

    results = sorted(results, key=lambda x: x["score"], reverse=True)[:args.top_k]

    print("\n=== FINAL RANKING ===\n")
    for r in results:
        print(f"{r['name']} → {r['score']}")

    print_insights(results)

    pd.DataFrame(results).to_csv(args.output_file, index=False)
    print(f"\nSaved results to: {args.output_file}")

    os.makedirs("audit_logs", exist_ok=True)
    for r in results:
        audit = r.get("audit", {})
        raw = audit.get("raw_response", {})
        if raw:
            out_file = os.path.join("audit_logs", f"{r['name']}_audit.json")
            with open(out_file, "w") as f:
                import json
                json.dump({
                    "name": r["name"],
                    "file": r["file"],
                    "raw_response": raw,
                    "cleaned_missing_skills": audit.get("cleaned_missing_skills", []),
                    "parsed_resume_skills": audit.get("parsed_resume_skills", [])
                }, f, indent=2)


if __name__ == "__main__":
    main()