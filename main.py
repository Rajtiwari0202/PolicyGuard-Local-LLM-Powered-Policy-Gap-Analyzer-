from __future__ import annotations

import argparse
import json
from pathlib import Path

from gap_detector import analyze_policy, build_gap_report
from llm_rewriter import rewrite_policy
from policy_reader import read_policy


def run_analysis(policy_path: str, domain: str, output_dir: str = "outputs") -> dict:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    policy_text = read_policy(policy_path)
    analysis = analyze_policy(policy_text, domain)
    improved_policy = rewrite_policy(policy_text, analysis["gaps"], domain)

    gap_report = build_gap_report(analysis)
    final_report = "\n\n".join([
        gap_report,
        "IMPROVED POLICY",
        improved_policy,
    ])

    (output_path / "analysis.json").write_text(json.dumps(analysis, indent=2), encoding="utf-8")
    (output_path / "gaps_report.txt").write_text(gap_report, encoding="utf-8")
    (output_path / "compliance_score.txt").write_text(f"{analysis['score']}%\n", encoding="utf-8")
    (output_path / "improved_policy.txt").write_text(improved_policy, encoding="utf-8")
    (output_path / "final_report.txt").write_text(final_report, encoding="utf-8")

    return analysis


def main() -> None:
    parser = argparse.ArgumentParser(description="Offline policy gap analyzer powered by local LLM workflows.")
    parser.add_argument("--policy", default="sample_policy.txt", help="Path to a TXT policy document.")
    parser.add_argument("--domain", default="Patch Management", help="Policy domain label.")
    parser.add_argument("--output-dir", default="outputs", help="Directory where reports will be written.")
    args = parser.parse_args()

    analysis = run_analysis(args.policy, args.domain, args.output_dir)
    print("PolicyGuard analysis complete")
    print(f"Score: {analysis['score']}%")
    print(f"Readiness: {analysis['readiness']}")
    print(f"Missing controls: {analysis['summary']['missing']}")
    print(f"Reports written to: {args.output_dir}")


if __name__ == "__main__":
    main()
