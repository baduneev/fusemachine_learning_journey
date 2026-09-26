"""Meaningful regression checks for guardrails, recovery, accounting and grading."""
import json
from pathlib import Path
import unittest
from unittest.mock import patch
from app.agentic.core import Agent
from app.agentic.documents import Documents
from app.agentic.providers import GeminiModel
from evaluation.replay import ReplayModel, action
from evaluation.run import grade

ROOT = Path(__file__).resolve().parent


class SequenceModel:
    usage_kind = "synthetic_unit_test_usage"
    def __init__(self, actions):
        self.actions = iter(actions)
    def decide(self, system, context):
        return next(self.actions), {"input_tokens":10,"output_tokens":5,"total_tokens":18,"thought_tokens":3}


class AgentTests(unittest.TestCase):
    def setUp(self):
        self.docs = Documents.from_json(ROOT / "corpus.json")
        self.claim = {"text":"Playwright controls Chromium.","source_id":"E1",
                      "quote":"The runner shall launch and control Chromium through Playwright."}

    def test_finish_requires_verification(self):
        result = Agent(SequenceModel([action("finish")]), self.docs, 1).run("Framework?")
        self.assertEqual(result.status,"max_steps")
        self.assertEqual(result.trajectory[0]["observation"]["error"],"unverified_finish")

    def test_finish_uses_verified_snapshot(self):
        sequence = [action("read_source",source="sample.pdf",page=6),action("verify_claims",claims=[self.claim]),action("finish")]
        result = Agent(SequenceModel(sequence),self.docs,3).run("Framework?")
        self.assertEqual(result.status,"completed")
        self.assertEqual(result.claims,[self.claim])

    def test_finish_rejects_unverified_claim_arguments(self):
        sequence = [action("read_source",source="sample.pdf",page=6),action("verify_claims",claims=[self.claim]),action("finish",claims=[self.claim])]
        result = Agent(SequenceModel(sequence),self.docs,3).run("Framework?")
        self.assertEqual(result.status,"max_steps")
        self.assertEqual(result.trajectory[-1]["action"],"invalid_action")

    def test_fabricated_quote_is_rejected_and_repaired(self):
        result = Agent(ReplayModel("revision"),self.docs).run("Verify Selenium")
        self.assertEqual(result.status,"completed")
        self.assertIn("Playwright",result.answer)
        self.assertTrue(any(t["action"]=="verify_claims" and not t["ok"] for t in result.trajectory))

    def test_unknown_citation_rejected(self):
        claim={**self.claim,"source_id":"FAKE"}
        result=Agent(SequenceModel([action("verify_claims",claims=[claim])]),self.docs,1).run("Framework?")
        self.assertFalse(result.trajectory[0]["ok"])

    def test_new_search_invalidates_verified_snapshot(self):
        seq=[action("read_source",source="sample.pdf",page=6),action("verify_claims",claims=[self.claim]),action("search_documents",query="Tier 3"),action("finish")]
        self.assertEqual(Agent(SequenceModel(seq),self.docs,4).run("Framework?").status,"max_steps")

    def test_unknown_action_and_wrong_argument_type(self):
        for invalid in [action("execute_shell",command="anything"),action("read_source",source="sample.pdf",page=True),action("search_documents",query="")]:
            with self.subTest(invalid=invalid):
                r=Agent(SequenceModel([invalid]),self.docs,1).run("Q")
                self.assertEqual(r.trajectory[0]["action"],"invalid_action")

    def test_source_path_not_executed(self):
        r=Agent(SequenceModel([action("read_source",source="../../secret",page=1)]),self.docs,1).run("Q")
        self.assertEqual(r.trajectory[0]["observation"]["error"],"tool_failure")

    def test_malformed_batch_is_discarded(self):
        r=Agent(ReplayModel("malformed"),self.docs,failure="malformed_once").run("Framework?")
        self.assertEqual(r.status,"completed")
        self.assertEqual(r.trajectory[0]["observation"]["error"],"tool_failure")
        self.assertEqual(len(r.evidence),1)

    def test_timeout_abstains(self):
        r=Agent(ReplayModel("timeout"),self.docs,failure="search_unavailable").run("Framework?")
        self.assertEqual(r.status,"abstained")
        self.assertFalse(r.claims)

    def test_iteration_cap(self):
        r=Agent(ReplayModel("step_limit"),self.docs).run("Budget?")
        self.assertEqual((r.status,len(r.trajectory)),("max_steps",8))

    def test_provider_total_includes_more_than_input_output(self):
        r=Agent(SequenceModel([action("clarify",question="Which system?")]),self.docs).run("Q")
        self.assertEqual(r.usage["total_tokens"],18)
        self.assertEqual(r.usage["input_tokens"],10)

    def test_missing_usage_not_faked(self):
        r=Agent(ReplayModel("model_failure"),self.docs).run("Q")
        self.assertIsNone(r.usage["total_tokens"])
        self.assertFalse(r.usage["accounting_complete"])

    def test_fixture_quotes_match_real_week15_pdf(self):
        from pypdf import PdfReader
        pages=PdfReader(ROOT.parent / "data/documents/sample.pdf").pages
        for d in self.docs.records:
            if d["source"]=="sample.pdf":
                self.assertIn(d["text"]," ".join(pages[d["page"]-1].extract_text().split()))

    def test_failure_taxonomy_detects_soft_and_cascading(self):
        cases=json.loads((ROOT/"cases.json").read_text())
        case=next(c for c in cases if c["id"]=="simple")
        r=Agent(ReplayModel("simple"),self.docs).run(case["query"])
        r.answer="Wrong framework"
        self.assertEqual(grade(case,r)["failure_category"],"soft_failure")
        r.trajectory.insert(0,{"action":"invalid_action","ok":False})
        self.assertEqual(grade(case,r)["failure_category"],"cascading_soft_failure")

    def test_revision_rubric_rejects_unsupported_exclusion(self):
        cases=json.loads((ROOT/"cases.json").read_text())
        case=next(c for c in cases if c["id"]=="revision")
        r=Agent(ReplayModel("revision"),self.docs).run(case["query"])
        r.answer="Playwright, not Selenium, controls Chromium."
        self.assertFalse(grade(case,r)["checks"]["answer_content"])

    def test_gemini_rest_contract_and_usage(self):
        # Mock only HTTP: validate parser, payload, timeout, and hidden thought filtering.
        import io
        response={"candidates":[{"content":{"parts":[{"text":"private","thought":True},{"text":json.dumps(action("clarify",question="Which system?"))}]}}],
                  "usageMetadata":{"promptTokenCount":12,"candidatesTokenCount":7,"thoughtsTokenCount":3,"totalTokenCount":22}}
        with patch.dict("os.environ",{"GEMINI_API_KEY":"test-only","GEMINI_MODEL":"test-model"}),patch("app.agentic.providers.urlopen",return_value=io.BytesIO(json.dumps(response).encode())) as send:
            raw,usage=GeminiModel().decide("system",{"question":"Q"})
            self.assertEqual(json.loads(raw)["action"],"clarify")
            self.assertEqual(usage["total_tokens"],22)
            self.assertEqual(send.call_args.kwargs["timeout"],45)
            request=send.call_args.args[0]
            self.assertEqual(json.loads(request.data)["generationConfig"]["responseMimeType"],"application/json")


if __name__ == "__main__":
    unittest.main()
