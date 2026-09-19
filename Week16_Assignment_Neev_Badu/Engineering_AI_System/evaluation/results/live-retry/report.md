# Week 16 evaluation results

Mode: **live**. Model: **gemini-3.5-flash-lite**.

Live Gemini results on the controlled excerpt corpus. These measure the model-controlled loop, not full-PDF/Chroma retrieval. Token values come from provider usage metadata; missing usage is unknown.

- Task completion (verified factual answer): 100%
- Expected behavior, including safe clarification/abstention: 100%
- Tool-call correctness: 100.0%
- Mean trajectory length: 3.0 iterations

| Case | Status | Behavior | Steps | Correct calls | Total tokens | Failure class |
|---|---|---|---:|---:|---:|---|
| revision | completed | PASS | 3 | 2/2 | 1773 | - |

## Interpretation

Tool correctness checks the case-specific allowed tool set and argument validity; a correct call can still fail because of an injected timeout. Claim correctness is scored separately. These checks are transparent heuristics, not a semantic judge. Required terms can miss paraphrases; review live traces manually.

Inspect each saved trajectory for chosen actions, rejected claims, failure observations, and recovery. Review completed answers for semantic support; rubric checks alone do not prove correctness.

Hard failures remain in the failure log even when safe handling passes. Normal clarification and evidence-based abstention are expected outcomes rather than system failures. Recovered invalid intermediate claims are logged in the full trajectory; unsuccessful downstream outputs are classified as soft or cascading soft failures.

## Live status

This report records a live-mode run; inspect error rows for any failed provider calls. Cost estimates are present only when usage is complete and prices were supplied.
No multi-agent baseline is needed because this is a single-agent system.
