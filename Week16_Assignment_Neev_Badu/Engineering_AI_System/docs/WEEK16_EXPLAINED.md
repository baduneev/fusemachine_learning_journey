# Week 16: what was asked and how it was done

Student: Neev Badu | Fusemachines | Task 3: Agentify the Assistant

## Requirement-to-deliverable mapping

| Assignment requirement | Implementation / evidence |
|---|---|
| Extend the W15 assistant | Original Python modules and sample PDF retained; `app/agentic/` adds the feature and reuses W15 Chroma/reranker through `W15Documents` |
| Explain why a fixed pipeline is insufficient before coding | `docs/DESIGN_DECISIONS.md` records the decision before the implementation |
| Model chooses next action from previous results | `Agent.run()` calls `model.decide()` each iteration; next action is not selected by application routing rules |
| More than one iteration, optional clarification, finite stop | Search, inspect, verify, revise, clarify, abstain, finish; default eight decisions, configurable from one to twenty |
| Context engineering | Three results per tool call, 900 characters per evidence item; eight evidence items and three recent actions in the next prompt |
| Single-agent or multi-agent justification | Single-agent sequential research; avoids unnecessary coordination and extra token use |
| Evaluation from scratch | `evaluation/run.py`; simple Python scoring, JSON traces, Markdown report, failure log |
| Completion rate | Verified factual answers divided by all queries; expected behavior is reported separately so abstentions are visible |
| Tool correctness | Case-specific allowed tools, argument schemas, valid page reads; injected tool outages are not counted as invalid model arguments |
| Trajectory length | Every model decision, including invalid output and finalization, counts as one iteration |
| Failure classes | Hard, soft, cascading soft classifications; unit tests check the latter two explicitly |
| Token and cost accounting | Per-call Gemini usage metadata summed per query; reasoning tokens retained; optional price inputs; unreported usage is unknown rather than zero |
| Failure injection | Search timeout and malformed retrieval; malformed batches never become evidence |
| Skill vs agent/tool decisions | One sentence per new capability in the pre-implementation document |
| Tool/agent boundary | Local stateful Chroma is exposed as a bounded retrieval call, not a collaborating agent |
| Updated diagram | `docs/architecture.png`, `.svg`, `.dot`, and `.mmd` |
| Approximately one-page assessed write-up | The seven labeled sections in the main README |

## Understand the change

W15 normally retrieves evidence once and generates an answer. W16 receives an observation, asks the model what action to take, executes that action, and returns the result to the model. The model may discover that one requirement is still missing, search again for it, inspect a particular page, or correct a draft before finishing.

For example: “When is Tier 3 used, and when must automatic healing be rejected?”

1. Search for Tier 3 and deterministic resolution.
2. Notice that rejection conditions still need evidence; search for confidence and ambiguity.
3. Propose two claims with supporting quotations and verify the quotations.
4. Finish with the verified claims and citations.

This four-decision example is present in the offline trace. In live mode, Gemini decides the actual order and number of actions; it is not forced to follow those four steps.

## Important limits

- The quote validator proves that the quotation exists in retrieved evidence. It does **not** prove that the interpretation is correct. Semantic checking remains the model's responsibility; this is a known single-agent self-verification limitation.
- The bundled evaluation uses four verified excerpts from the existing `sample.pdf` and two clearly labeled synthetic conflicting policies. Synthetic policies are evaluation data only; the production PDF CLI never loads them.
- The delivered tests use `ReplayModel`, a test double. Their pass rate is software behavior evidence, not a measured Gemini accuracy score.
- Gemini was called against the live service for a PDF CLI smoke test and the eight-case controlled-corpus evaluation. The currently saved full live run passed four of eight expected-behavior checks; three calls stopped on HTTP 429, and one correction failed its content rubric. A separate correction retry passed. Live token counts are in the reports, while monetary cost remains unknown without a supplied model price. The heavyweight Chroma integration was not run in this environment.
- The lexical PDF backend runs without embedding downloads. The Chroma backend preserves the W15 top-10 retrieval / top-3 reranking design. A source filter on that path applies within the retrieved candidate set, so `read_source` is useful when a particular known page is needed.
- Large collections can exceed the 40-source catalog cap; this assignment targets a small document collection. Retrieval truncation can omit useful evidence, so the agent may need a more focused search or safely abstain.
- JSON trace files can contain document excerpts. Keep private-document traces out of public repositories.

## Short explanation in Nepali

- **के मागेको थियो?** पुरानो assistant लाई यस्तो बनाउने कि अघिल्लो search को result हेरेर अब के गर्ने भन्ने model आफैंले निर्णय गरोस्।
- **के बनाइयो?** Evidence जाँच्ने single-agent loop: search → result हेर्ने → आवश्यक भए फेरि search वा page पढ्ने → claim verify गर्ने → answer दिने।
- **किन loop चाहियो?** पहिलो search मै सबै प्रमाण नआउन सक्छ; गलत वा अपूरो प्रमाण भेटिएपछि अर्को कदम बदल्नुपर्छ।
- **कसरी रोक्छ?** बढीमा ८ decisions; प्रमाण नपुगे clarification वा abstention दिन्छ।
- **Testing के भयो?** वास्तविक loop र tools लाई offline test double बाट जाँचियो। अहिले सुरक्षित गरिएको Gemini live report मा आठमध्ये चार case सफल भए; तीनवटा HTTP 429 ले रोकिए। छुट्टै correction rerun सफल भयो।

## Demo / viva talking points

1. Agentic behavior means the model selects actions after observations, not merely repeated RAG calls.
2. A tool performs one bounded operation; the agent decides which operation is useful next.
3. Context capping controls repeated evidence growth while a full external trace remains available for debugging.
4. The failure test exposes a tool error to the model; it cannot silently promote malformed data into evidence.
5. Safe abstention can pass the behavior check while lowering factual task completion. Report both metrics.
6. Multi-agent was deliberately unnecessary: the retrieval and verification decisions depend on each other, and extra agents would add coordination cost.

## API implementation references

- [Gemini generateContent REST reference](https://ai.google.dev/api/generate-content)
- [Gemini token usage accounting](https://ai.google.dev/gemini-api/docs/tokens)

The REST request and usage parser follow these interfaces. Model IDs and prices are configuration values, not guessed constants.
