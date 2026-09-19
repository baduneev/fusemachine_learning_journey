"""Run from project root: python -m evaluation.run [--mode live]."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import statistics
import time

from app.agentic.core import Agent
from app.agentic.documents import Documents
from app.agentic.providers import GeminiModel
from evaluation.replay import ReplayModel

ROOT = Path(__file__).resolve().parent
TOOLS = {"search_documents", "read_source", "verify_claims"}


def grade(case, result):
    text = result.answer.lower()
    cited = [result.evidence[c["source_id"]] for c in result.claims if c["source_id"] in result.evidence]
    checks = {
        "expected_status": result.status in case["expected_status"],
        "answer_content": all(t.lower() in text for t in case.get("required_terms", []))
                          and not any(t.lower() in text for t in case.get("forbidden_terms", [])),
        "required_pages": set(case.get("required_pages", [])) <= {d["page"] for d in cited},
        "required_sources": set(case.get("required_sources", [])) <= {d["source"] for d in cited},
        "reasonable_trajectory": case["min_steps"] <= len(result.trajectory) <= case["max_steps"],
        "citation_integrity": all(" ".join(c["quote"].split()) in " ".join(result.evidence.get(c["source_id"],{}).get("text", "").split()) for c in result.claims),
    }
    if result.status == "completed":
        checks["verified_finish"] = bool(result.claims) and any(t["action"] == "verify_claims" and t["ok"] for t in result.trajectory)
    if case.get("failure"):
        checks["injection_observed"] = any(t.get("observation", {}).get("error") == "tool_failure" for t in result.trajectory)
        checks["safe_failure_response"] = (result.status in {"abstained", "clarification"}
            or result.status == "completed" and bool(result.claims)
            and all(c["source_id"] in result.evidence for c in result.claims))
    calls = [t for t in result.trajectory if t["action"] in TOOLS or t["action"] == "invalid_action"]
    correct = sum(t["action"] in case["allowed_tools"] and t.get("arguments_valid", False)
                  and (t["action"] != "read_source" or t.get("ok", False)) for t in calls)
    success = all(checks.values())
    incidents = [t for t in result.trajectory if not t.get("ok", False)]
    # Hard: runtime/tool failure or exhausted budget prevented an answer.
    # Soft: completed/terminated but failed content, action or trajectory checks.
    # Cascading soft: earlier invalid intermediate result followed by a bad final outcome.
    failure = None
    if result.status in {"error", "max_steps"} or (case.get("failure") and result.status == "abstained"):
        failure = "hard_failure"
    elif not success:
        failure = "cascading_soft_failure" if incidents else "soft_failure"
    return {"checks": checks, "behavior_pass": success,
            "task_completed": result.status == "completed" and success,
            "correct_tool_calls": correct, "tool_calls": len(calls),
            "failure_category": failure, "recovered_incidents": len(incidents) if success and result.status == "completed" else 0}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["offline", "live"], default="offline")
    parser.add_argument("--case", help="Run one case ID (useful for a failed live case)")
    parser.add_argument("--model")
    parser.add_argument("--output", help="Output directory; defaults to evaluation/results/<mode>")
    parser.add_argument("--delay-seconds", type=float, default=0,
                        help="Pause between live cases to respect model rate limits")
    parser.add_argument("--input-usd-per-million", type=float)
    parser.add_argument("--output-usd-per-million", type=float)
    args = parser.parse_args()
    if any(v is not None and v < 0 for v in (args.input_usd_per_million, args.output_usd_per_million, args.delay_seconds)):
        parser.error("Prices and delay must be nonnegative")
    try:
        live_model = GeminiModel(args.model) if args.mode == "live" else None
    except ValueError as exc:
        parser.error(str(exc))
    docs = Documents.from_json(ROOT / "corpus.json")
    cases = json.loads((ROOT / "cases.json").read_text())
    if args.case:
        cases = [case for case in cases if case["id"] == args.case]
        if not cases:
            parser.error(f"Unknown case ID: {args.case}")
        if args.mode == "live" and cases[0].get("offline_only"):
            parser.error(f"Case {args.case} is offline only")
    rows = []
    for case in cases:
        if args.mode == "live" and case.get("offline_only"):
            continue
        if args.mode == "live" and rows and args.delay_seconds:
            time.sleep(args.delay_seconds)
        model = live_model or ReplayModel(case["id"])
        start = time.perf_counter()
        result = Agent(model, docs, failure=case.get("failure")).run(case["query"])
        row = {"id": case["id"], "query": case["query"], **grade(case, result),
               "seconds": round(time.perf_counter()-start, 4), **result.to_dict()}
        price_known = args.input_usd_per_million is not None and args.output_usd_per_million is not None
        if args.mode == "offline":
            row["estimated_cost_usd"] = 0.0
        elif price_known and result.usage["accounting_complete"]:
            # Billable output includes reported reasoning tokens. No cached prompts are configured.
            thought = sum(c.get("thought_tokens",0) for c in result.usage["calls"])
            row["estimated_cost_usd"] = (result.usage["input_tokens"]*args.input_usd_per_million
                +(result.usage["output_tokens"]+thought)*args.output_usd_per_million)/1_000_000
        else:
            row["estimated_cost_usd"] = None
        rows.append(row)
        print(f"{case['id']}: {result.status}; behavior={'PASS' if row['behavior_pass'] else 'FAIL'}; steps={len(result.trajectory)}")
    calls = sum(r["tool_calls"] for r in rows)
    summary = {"mode": args.mode, "model": live_model.model if live_model else "ReplayModel (test double)",
               "created_utc": datetime.now(timezone.utc).isoformat(), "queries": len(rows),
               "task_completion_rate": sum(r["task_completed"] for r in rows)/len(rows),
               "expected_behavior_rate": sum(r["behavior_pass"] for r in rows)/len(rows),
               "tool_call_correctness": sum(r["correct_tool_calls"] for r in rows)/calls if calls else None,
               "mean_trajectory_length": statistics.mean(len(r["trajectory"]) for r in rows),
               "pricing": {"input_usd_per_million": args.input_usd_per_million,"output_usd_per_million":args.output_usd_per_million}}
    output = Path(args.output) if args.output else ROOT / "results" / args.mode
    output.mkdir(parents=True, exist_ok=True)
    (output / "results.json").write_text(json.dumps({"summary":summary,"queries":rows},indent=2),encoding="utf-8")
    failures = [{"id":r["id"],"category":r["failure_category"],"status":r["status"],
                 "checks":r["checks"],
                 "http_statuses":[t["http_status"] for t in r["trajectory"] if "http_status" in t]}
                for r in rows if r["failure_category"]]
    (output / "failures.json").write_text(json.dumps(failures,indent=2),encoding="utf-8")
    report = ["# Week 16 evaluation results", "", f"Mode: **{args.mode}**. Model: **{summary['model']}**.", "",
              ("Offline results exercise the actual loop and document tools with a scripted test double. They do not measure LLM reasoning or live retrieval quality. Zero tokens means no model was called; unknown usage after a model error is null."
               if args.mode == "offline" else "Live Gemini results on the controlled excerpt corpus. These measure the model-controlled loop, not full-PDF/Chroma retrieval. Token values come from provider usage metadata; missing usage is unknown."), "",
              f"- Task completion (verified factual answer): {summary['task_completion_rate']:.0%}",
              f"- Expected behavior, including safe clarification/abstention: {summary['expected_behavior_rate']:.0%}",
              f"- Tool-call correctness: {summary['tool_call_correctness']:.1%}",
              f"- Mean trajectory length: {summary['mean_trajectory_length']:.1f} iterations", "",
              "| Case | Status | Behavior | Steps | Correct calls | Total tokens | Failure class |",
              "|---|---|---|---:|---:|---:|---|"]
    for r in rows:
        report.append(f"| {r['id']} | {r['status']} | {'PASS' if r['behavior_pass'] else 'FAIL'} | {len(r['trajectory'])} | {r['correct_tool_calls']}/{r['tool_calls']} | {r['usage']['total_tokens']} | {r['failure_category'] or '-'} |")
    report += ["", "## Interpretation", "",
               "Tool correctness checks the case-specific allowed tool set and argument validity; a correct call can still fail because of an injected timeout. Claim correctness is scored separately. These checks are transparent heuristics, not a semantic judge. Required terms can miss paraphrases; review live traces manually.", "",
               ("The revision case rejects a fabricated quote before accepting a corrected one. The malformed case discards the complete invalid batch and uses read_source. The timeout case exposes the tool error; the offline policy safely abstains. The cap case stops at eight decisions. Model failure returns an error without a factual answer."
                if args.mode == "offline" else "Inspect each saved trajectory for chosen actions, rejected claims, failure observations, and recovery. Review completed answers for semantic support; rubric checks alone do not prove correctness."), "",
               "Hard failures remain in the failure log even when safe handling passes. Normal clarification and evidence-based abstention are expected outcomes rather than system failures. Recovered invalid intermediate claims are logged in the full trajectory; unsuccessful downstream outputs are classified as soft or cascading soft failures.", "",
               "## Live status", "", ("This offline report contains no live-model measurements. Run `python -m evaluation.run --mode live` with credentials for a separate live report."
                if args.mode == "offline" else "This report records a live-mode run; inspect error rows for any failed provider calls. Cost estimates are present only when usage is complete and prices were supplied."),
               "No multi-agent baseline is needed because this is a single-agent system."]
    (output / "report.md").write_text("\n".join(report)+"\n",encoding="utf-8")
    if not all(r["behavior_pass"] for r in rows):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
