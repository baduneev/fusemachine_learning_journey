"""Run one golden regression set against every prompt and log Evidently results.

This is intentionally a live LLM-as-a-judge evaluation. Set GEMINI_API_KEY and
GEMINI_MODEL in the environment or in a local .env file; secrets are never
written to the generated artifacts.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv
import mlflow
import pandas as pd

from evidently import DataDefinition, Dataset, Report
from evidently.descriptors import CompletenessLLMEval, CorrectnessLLMEval
from evidently.llm.options import GeminiOptions
from evidently.presets import TextEvals
from evidently.tests import eq


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "mlops" / "outputs"
TRACKING_URI = f"sqlite:///{(ROOT / 'mlruns.db').as_posix()}"
VERSIONS = ("prompt_v1", "prompt_v2", "prompt_v3")


def load_regression_rows() -> pd.DataFrame:
    golden = json.loads((ROOT / "mlops" / "golden_set.json").read_text(encoding="utf-8"))
    rows = []
    for version in VERSIONS:
        for example in golden:
            trace_path = OUTPUT / version / f"trace_{example['case']}.json"
            trace = json.loads(trace_path.read_text(encoding="utf-8"))
            rows.append(
                {
                    "prompt_version": version,
                    **example,
                    "answer": trace["answer"],
                    "agent_status": trace["status"],
                    "human_expected_pass": bool(trace["passed"]),
                }
            )
    return pd.DataFrame(rows)


def evaluate(frame: pd.DataFrame, api_key: str, model: str) -> tuple[Dataset, pd.DataFrame]:
    descriptors = [
        CorrectnessLLMEval(
            "answer",
            target_output="golden_response",
            provider="gemini",
            model=model,
            alias="Reference correctness",
            include_category=True,
            include_score=True,
            include_reasoning=True,
            tests=[eq("CORRECT", column="Reference correctness", alias="Correctness pass")],
        ),
        CompletenessLLMEval(
            "answer",
            context="source_context",
            provider="gemini",
            model=model,
            alias="Answer completeness",
            include_category=True,
            include_score=True,
            include_reasoning=True,
            tests=[eq("COMPLETE", column="Answer completeness", alias="Completeness pass")],
        ),
    ]
    dataset = Dataset.from_pandas(
        frame,
        data_definition=DataDefinition(),
        descriptors=descriptors,
        options=[GeminiOptions(api_key=api_key, rpm_limit=8)],
    )
    result = dataset.as_dataframe().copy()
    result["all_tests_pass"] = result["Correctness pass"] & result["Completeness pass"]
    return dataset, result


def write_report(dataset: Dataset, result: pd.DataFrame, model: str) -> pd.DataFrame:
    report = Report(
        [
            TextEvals(
                columns=[
                    "Reference correctness",
                    "Reference correctness score",
                    "Answer completeness",
                    "Answer completeness score",
                    "Correctness pass",
                    "Completeness pass",
                ],
                include_tests=True,
            )
        ],
        metadata={"judge_provider": "Gemini", "judge_model": model},
        tags=["week17", "llm-regression", "golden-set"],
    )
    snapshot = report.run(dataset)
    snapshot.save_html(str(OUTPUT / "evidently_llm_regression.html"))
    snapshot.save_json(str(OUTPUT / "evidently_llm_regression.json"))
    result.to_csv(OUTPUT / "llm_judge_row_results.csv", index=False)

    summary = (
        result.groupby("prompt_version", as_index=False)
        .agg(
            cases=("case", "count"),
            correctness_pass_rate=("Correctness pass", "mean"),
            completeness_pass_rate=("Completeness pass", "mean"),
            all_tests_pass_rate=("all_tests_pass", "mean"),
        )
        .sort_values("prompt_version")
    )
    summary.to_csv(OUTPUT / "llm_regression_summary.csv", index=False)
    (OUTPUT / "llm_regression_summary.md").write_text(
        summary.to_markdown(index=False, floatfmt=".4f") + "\n", encoding="utf-8"
    )
    agreement = float((result["all_tests_pass"] == result["human_expected_pass"]).mean())
    sanity = {
        "method": "Compare the joint judge verdict with a human-authored expected pass label for every row.",
        "agreement_rate": agreement,
        "rows_checked": int(len(result)),
        "interpretation": (
            "The judge agrees with all human labels in this small set."
            if agreement == 1.0
            else "Review disagreements in llm_judge_row_results.csv before trusting the judge as a gate."
        ),
    }
    (OUTPUT / "judge_sanity_check.json").write_text(json.dumps(sanity, indent=2), encoding="utf-8")
    return summary


def log_to_mlflow(summary: pd.DataFrame) -> None:
    mlflow.set_tracking_uri(TRACKING_URI)
    comparison = pd.read_csv(OUTPUT / "prompt_comparison.csv")
    for row in summary.to_dict(orient="records"):
        run_id = comparison.loc[
            comparison.prompt_version == row["prompt_version"], "run_id"
        ].iloc[0]
        with mlflow.start_run(run_id=run_id):
            mlflow.log_metrics(
                {
                    "llm_judge_correctness_pass_rate": row["correctness_pass_rate"],
                    "llm_judge_completeness_pass_rate": row["completeness_pass_rate"],
                    "llm_regression_tests_passed_pct": 100.0 * row["all_tests_pass_rate"],
                }
            )
            mlflow.log_artifact(str(OUTPUT / "evidently_llm_regression.html"), artifact_path="llm_regression")
            mlflow.log_artifact(str(OUTPUT / "llm_judge_row_results.csv"), artifact_path="llm_regression")


def main() -> None:
    load_dotenv(ROOT / ".env")
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    model = os.getenv("GEMINI_MODEL", "").strip()
    if not api_key or not model:
        raise SystemExit("Set GEMINI_API_KEY and GEMINI_MODEL in track_b_agent/.env or the environment.")
    frame = load_regression_rows()
    dataset, result = evaluate(frame, api_key, model)
    summary = write_report(dataset, result, model)
    log_to_mlflow(summary)
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
