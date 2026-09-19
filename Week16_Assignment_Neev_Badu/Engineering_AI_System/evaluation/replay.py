"""Explicit test double. NOT an LLM, and never used by the production CLI.

Scripts exercise production Agent and Documents; observed verification/tool
errors control recovery branches. These are regression tests, not AI-quality scores.
"""
import copy


def action(name, **args):
    return {"action": name, "args": args, "note": "Offline test-double action"}


class ReplayModel:
    usage_kind = "offline_no_model_calls"

    def __init__(self, case_id):
        self.case_id, self.calls = case_id, 0
        self.bad_claim_sent = False

    def decide(self, system, context):
        self.calls += 1
        obs = context["observation"]
        evidence = context["evidence"]
        cid = self.case_id
        if cid == "model_failure":
            raise TimeoutError("Injected model failure")
        if cid == "clarification":
            result = action("clarify", question="Which options and evaluation criteria should I compare?")
        elif cid == "step_limit":
            result = action("search_documents", query="annual hosting budget")
        elif obs.get("error") == "tool_failure":
            if cid == "timeout":
                result = action("abstain", reason="Search is unavailable, so I cannot verify the requested framework.")
            else:
                result = action("read_source", source="sample.pdf", page=6)
        elif cid == "unsupported":
            result = (action("search_documents", query="annual hosting budget Nepalese rupees")
                      if self.calls == 1 else action("abstain", reason="The documents do not specify an annual hosting budget."))
        elif not evidence:
            query = {"research": "Tier 3 enabled deterministic", "conflict": "review timeout"}.get(cid, "Chromium Playwright")
            args = {"query": query}
            if cid == "conflict":
                args["source"] = "synthetic_old_policy.txt"
            result = action("search_documents", **args)
        elif cid == "research" and not any(e["page"] == 8 for e in evidence):
            result = action("search_documents", query="automatic healing confidence ambiguous")
        elif cid == "conflict" and not any(e["source"] == "synthetic_new_policy.txt" for e in evidence):
            result = action("read_source", source="synthetic_new_policy.txt", page=1)
        else:
            if cid == "research":
                chosen = [next(e for e in evidence if e["page"] == p) for p in (7,8)]
            elif cid == "conflict":
                chosen = [next(e for e in evidence if e["source"] == s) for s in ("synthetic_old_policy.txt","synthetic_new_policy.txt")]
            else:
                chosen = [next(e for e in evidence if e["source"] == "sample.pdf" and e["page"] == 6)]
            claims = [{"text": e["text"], "source_id": e["source_id"], "quote": e["text"]} for e in chosen]
            if cid == "revision" and not self.bad_claim_sent:
                self.bad_claim_sent = True
                claims[0]["text"] = "Selenium controls Chromium."
                claims[0]["quote"] = "Selenium controls Chromium."
                result = action("verify_claims", claims=claims)
            elif obs.get("valid"):
                result = action("finish")
            else:
                result = action("verify_claims", claims=claims)
        return copy.deepcopy(result), {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
