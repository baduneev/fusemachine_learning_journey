"""Deterministic prompt-policy replay for reproducible delivered MLflow artifacts.

Live mode remains available through GeminiModel. This test provider makes prompt
failure branches repeatable without presenting its scores as live LLM quality.
"""
import copy

from evaluation.replay import action


class VersionedReplayModel:
    usage_kind = "synthetic_prompt_experiment_tokens"

    def __init__(self, version, case_id):
        self.version, self.case_id, self.calls = version, case_id, 0

    def _claims(self, evidence):
        if self.case_id == "research":
            selected = [next(e for e in evidence if e["page"] == p) for p in (7, 8) if any(x["page"] == p for x in evidence)]
        else:
            selected = [next(e for e in evidence if e["source"] == "sample.pdf" and e["page"] == 6)]
        return [{"text": e["text"], "source_id": e["source_id"], "quote": e["text"]} for e in selected]

    def decide(self, system, context):
        self.calls += 1
        obs, evidence = context["observation"], context["evidence"]
        note = f"{self.version} observed {list(obs)[:2]} and selected the next bounded action"
        if self.version == "prompt_v1":
            if not evidence:
                result = action("search_documents", query=context["question"])
            else:
                result = action("finish")
        elif self.version == "prompt_v2":
            if obs.get("error") == "tool_failure":
                result = action("abstain", reason="The search tool failed, so evidence is unavailable.")
            elif self.case_id == "unsupported" and self.calls > 1:
                result = action("abstain", reason="The documents do not specify an annual hosting budget.")
            elif not evidence:
                result = action("search_documents", query=context["question"])
            elif self.case_id == "revision" and not obs.get("problems"):
                bad = self._claims(evidence)
                bad[0] = {"text": "Selenium controls Chromium.", "source_id": bad[0]["source_id"],
                          "quote": "Selenium controls Chromium."}
                result = action("verify_claims", claims=bad)
            elif obs.get("valid"):
                result = action("finish")
            elif obs.get("problems"):
                result = action("abstain", reason="The initial correction could not be verified.")
            else:
                result = action("verify_claims", claims=self._claims(evidence))
        else:
            if obs.get("error") == "tool_failure":
                result = action("read_source", source="sample.pdf", page=6)
            elif self.case_id == "unsupported" and self.calls > 1:
                result = action("abstain", reason="The documents do not specify an annual hosting budget.")
            elif not evidence:
                query = {"research": "Tier 3 enabled deterministic", "revision": "Chromium Playwright"}.get(
                    self.case_id, context["question"])
                result = action("search_documents", query=query)
            elif self.case_id == "research" and not any(e["page"] == 8 for e in evidence):
                result = action("search_documents", query="automatic healing confidence ambiguous")
            elif obs.get("valid"):
                result = action("finish")
            else:
                result = action("verify_claims", claims=self._claims(evidence))
        result["note"] = note
        # Stable token proxy makes configuration cost visible in offline runs.
        usage = {"input_tokens": max(1, (len(system) + context["remaining_steps"] * 10) // 4),
                 "output_tokens": max(1, len(str(result)) // 4)}
        usage["total_tokens"] = usage["input_tokens"] + usage["output_tokens"]
        return copy.deepcopy(result), usage

