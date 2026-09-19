# Week 16 evaluation results

Mode: **offline**. Model: **ReplayModel (test double)**.

Offline results exercise the actual loop and document tools with a scripted test double. They do not measure LLM reasoning or live retrieval quality. Zero tokens means no model was called; unknown usage after a model error is null.

- Task completion (verified factual answer): 50%
- Expected behavior, including safe clarification/abstention: 100%
- Tool-call correctness: 100.0%
- Mean trajectory length: 3.3 iterations

| Case | Status | Behavior | Steps | Correct calls | Total tokens | Failure class |
|---|---|---|---:|---:|---:|---|
| simple | completed | PASS | 3 | 2/2 | 0 | - |
| research | completed | PASS | 4 | 3/3 | 0 | - |
| revision | completed | PASS | 4 | 3/3 | 0 | - |
| clarification | clarification | PASS | 1 | 0/0 | 0 | - |
| unsupported | abstained | PASS | 2 | 1/1 | 0 | - |
| conflict | completed | PASS | 4 | 3/3 | 0 | - |
| timeout | abstained | PASS | 2 | 1/1 | 0 | hard_failure |
| malformed | completed | PASS | 4 | 3/3 | 0 | - |
| step_limit | max_steps | PASS | 8 | 8/8 | 0 | hard_failure |
| model_failure | error | PASS | 1 | 0/0 | None | hard_failure |

## Interpretation

Tool correctness checks the case-specific allowed tool set and argument validity; a correct call can still fail because of an injected timeout. Claim correctness is scored separately. These checks are transparent heuristics, not a semantic judge. Required terms can miss paraphrases; review live traces manually.

The revision case rejects a fabricated quote before accepting a corrected one. The malformed case discards the complete invalid batch and uses read_source. The timeout case exposes the tool error; the offline policy safely abstains. The cap case stops at eight decisions. Model failure returns an error without a factual answer.

Hard failures remain in the failure log even when safe handling passes. Normal clarification and evidence-based abstention are expected outcomes rather than system failures. Recovered invalid intermediate claims are logged in the full trajectory; unsuccessful downstream outputs are classified as soft or cascading soft failures.

## Live status

This offline report contains no live-model measurements. Run `python -m evaluation.run --mode live` with credentials for a separate live report.
No multi-agent baseline is needed because this is a single-agent system.
