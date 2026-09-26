import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "mlops" / "outputs"


def test_each_prompt_has_five_complete_traces():
    for version in ("prompt_v1", "prompt_v2", "prompt_v3"):
        traces = sorted((OUTPUT / version).glob("trace_*.json"))
        assert len(traces) == 5
        for path in traces:
            trace = json.loads(path.read_text(encoding="utf-8"))
            assert trace["termination_reason"] == trace["status"]
            assert trace["trajectory"]
            assert all("action" in step and "note" in step for step in trace["trajectory"])
            for step in trace["trajectory"]:
                if step["action"] in {"search_documents", "read_source", "verify_claims"} and step.get("ok"):
                    assert "raw_result" in step


def test_golden_set_is_identical_across_prompt_versions():
    expected = {item["case"] for item in json.loads((ROOT / "mlops" / "golden_set.json").read_text())}
    rows = pd.read_csv(OUTPUT / "llm_judge_row_results.csv")
    assert set(rows.prompt_version) == {"prompt_v1", "prompt_v2", "prompt_v3"}
    for _, group in rows.groupby("prompt_version"):
        assert set(group.case) == expected


def test_promoted_prompt_passes_delivered_behavior_and_llm_gates():
    behavior = pd.read_csv(OUTPUT / "prompt_comparison.csv").set_index("prompt_version")
    judge = pd.read_csv(OUTPUT / "llm_regression_summary.csv").set_index("prompt_version")
    assert behavior.loc["prompt_v3", "behavior_pass_rate"] == 1.0
    assert judge.loc["prompt_v3", "all_tests_pass_rate"] == 1.0
