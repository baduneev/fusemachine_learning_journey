"""Run three prompt/config versions, save full traces, and log comparison to MLflow."""
import json
from pathlib import Path
import shutil
import statistics

import mlflow
import pandas as pd

from app.agentic.core import Agent
from app.agentic.documents import Documents
from mlops.versioned_replay import VersionedReplayModel

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "mlops" / "outputs"
TRACKING_URI = f"sqlite:///{(ROOT / 'mlruns.db').as_posix()}"
CONFIGS = {
    "prompt_v1": {"max_steps": 4, "max_evidence": 4, "max_results": 2,
                  "diagnosis": "Unverified finish attempts caused step exhaustion."},
    "prompt_v2": {"max_steps": 6, "max_evidence": 6, "max_results": 3,
                  "diagnosis": "Verification improved, but incomplete multi-part research and failed correction recovery remained."},
    "prompt_v3": {"max_steps": 8, "max_evidence": 8, "max_results": 3,
                  "diagnosis": "Added targeted second search, verification repair, and alternate-tool recovery."},
}
CASES = [
    {"id": "simple", "query": "Which framework controls Chromium?", "expected": ["completed"], "terms": ["playwright"]},
    {"id": "research", "query": "When is Tier 3 used, and when must automatic healing be rejected?",
     "expected": ["completed"], "terms": ["enabled", "deterministic", "confidence", "ambiguous"]},
    {"id": "revision", "query": "Verify that Selenium controls Chromium and correct the claim.",
     "expected": ["completed"], "terms": ["playwright"], "forbidden": ["selenium controls", "not selenium"]},
    {"id": "unsupported", "query": "What is the documented annual hosting budget?",
     "expected": ["abstained"], "terms": ["do not specify"]},
    {"id": "timeout", "query": "Which framework controls Chromium after a search outage?",
     "expected": ["completed", "abstained"], "terms": ["playwright"], "failure": "search_unavailable"},
]


def grade(case, result):
    text = result.answer.lower()
    passed = (result.status in case["expected"] and all(term in text for term in case.get("terms", []))
              and not any(term in text for term in case.get("forbidden", [])))
    if result.status == "completed":
        passed = passed and bool(result.claims) and any(t["action"] == "verify_claims" and t.get("ok")
                                                       for t in result.trajectory)
    return passed


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    docs = Documents.from_json(ROOT / "evaluation" / "corpus.json")
    mlflow.set_tracking_uri(TRACKING_URI); mlflow.set_experiment("agent-prompt-comparison")
    summaries = []
    for version, config in CONFIGS.items():
        prompt_path = ROOT / "prompts" / f"{version}.txt"
        prompt = prompt_path.read_text(encoding="utf-8")
        version_dir = OUTPUT / version
        if version_dir.exists(): shutil.rmtree(version_dir)
        version_dir.mkdir(parents=True)
        rows = []
        with mlflow.start_run(run_name=version) as run:
            mlflow.log_params({"prompt_version": version, "provider": "VersionedReplayModel",
                               "temperature": 0, **{k: v for k, v in config.items() if k != "diagnosis"}})
            for case in CASES:
                result = Agent(VersionedReplayModel(version, case["id"]), docs,
                               max_steps=config["max_steps"], failure=case.get("failure"),
                               system_prompt=prompt, max_evidence=config["max_evidence"],
                               max_results=config["max_results"]).run(case["query"])
                passed = grade(case, result)
                record = {"case": case, "passed": passed,
                          "termination_reason": result.status, **result.to_dict()}
                trace_path = version_dir / f"trace_{case['id']}.json"
                trace_path.write_text(json.dumps(record, indent=2), encoding="utf-8")
                rows.append({"case": case["id"], "status": result.status, "passed": passed,
                             "iterations": len(result.trajectory), "total_tokens": result.usage["total_tokens"]})
            result_frame = pd.DataFrame(rows)
            result_frame.to_csv(version_dir / "case_results.csv", index=False)
            (version_dir / "diagnosis.txt").write_text(config["diagnosis"] + "\n", encoding="utf-8")
            metrics = {"behavior_pass_rate": float(result_frame.passed.mean()),
                       "task_completion_rate": float((result_frame.status == "completed").mean()),
                       "mean_iterations": float(result_frame.iterations.mean()),
                       "total_tokens": int(result_frame.total_tokens.sum())}
            mlflow.log_metrics(metrics)
            mlflow.log_artifact(str(prompt_path), artifact_path="prompt")
            mlflow.log_artifacts(str(version_dir), artifact_path="evaluation")
            summaries.append({"run_id": run.info.run_id, "prompt_version": version,
                              "diagnosis_from_previous_trace": config["diagnosis"], **metrics})
    comparison = pd.DataFrame(summaries)
    comparison.to_csv(OUTPUT / "prompt_comparison.csv", index=False)
    (OUTPUT / "prompt_comparison.md").write_text(comparison.to_markdown(index=False, floatfmt=".4f") + "\n", encoding="utf-8")
    best = comparison.sort_values(["behavior_pass_rate", "total_tokens"], ascending=[False, True]).iloc[0]
    (OUTPUT / "promotion_decision.json").write_text(json.dumps({
        "promoted_prompt": best.prompt_version, "rule": "highest behavior pass rate, then lowest total tokens",
        "behavior_pass_rate": float(best.behavior_pass_rate), "total_tokens": int(best.total_tokens),
        "provider_limitation": "Delivered comparison uses an explicit deterministic test provider; run live mode before production."}, indent=2), encoding="utf-8")
    print(comparison.to_string(index=False))


if __name__ == "__main__":
    main()
