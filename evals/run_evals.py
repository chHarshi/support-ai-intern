# evals/run_evals.py
import sys
import json
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent.parent))

from evals.triage_cases import build_triage_test_cases
from evals.account_cases import build_account_test_cases


def main():
    print("Running triage test cases...")
    triage_results = build_triage_test_cases()
    print("Running account brief test cases...")
    account_results = build_account_test_cases()

    all_results = triage_results + account_results

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_cases": len(all_results),
        "passed": sum(r.passed for r in all_results),
        "failed": sum(not r.passed for r in all_results),
        "average_score": round(sum(r.score for r in all_results) / len(all_results), 3),
        "results": [r.to_dict() for r in all_results],
    }

    out_path = Path(__file__).parent.parent / "eval_report.json"
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)

    # also write a readable markdown summary
    md_lines = [
        "# Eval Report",
        f"Generated: {report['generated_at']}",
        f"\n**{report['passed']}/{report['total_cases']} passed** | average score: {report['average_score']}\n",
        "| Case | Task | Score | Passed |",
        "|------|------|-------|--------|",
    ]
    for r in report["results"]:
        md_lines.append(f"| {r['case_id']} | {r['task']} | {r['score']} | {'✅' if r['passed'] else '❌'} |")
    md_lines.append("\n## Details\n")
    for r in report["results"]:
        md_lines.append(f"### {r['case_id']} ({r['task']}) — score {r['score']}")
        for c in r["checks"]:
            mark = "✅" if c["passed"] else "❌"
            md_lines.append(f"- {mark} {c['name']}" + (f" — {c['detail']}" if c["detail"] else ""))
        md_lines.append("")

    md_path = Path(__file__).parent.parent / "eval_report.md"
    md_path.write_text("\n".join(md_lines), encoding="utf-8")

    print(f"\nDone. {report['passed']}/{report['total_cases']} passed, avg score {report['average_score']}")
    print(f"Report written to: {out_path} and {md_path}")


if __name__ == "__main__":
    main()