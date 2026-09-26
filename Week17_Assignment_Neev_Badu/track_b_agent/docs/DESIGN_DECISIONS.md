# Pre-implementation decisions

**Why not a fixed pipeline?** A draft may reveal missing or contradictory evidence, so the model must decide whether to reformulate a search, inspect another page, revise a claim, ask a clarifying question, or abstain based on intermediate results.

**Skill vs agent:** A Skill can describe evidence checking, but cannot itself choose and execute an observation-dependent sequence of actions; one model-controlled loop is needed and additional agents are unnecessary for this small sequential task.

**Skill vs search_documents tool:** Search instructions could be a Skill, but accessing the document index requires executable retrieval, so this is a bounded tool.

**Skill vs read_source tool:** A Skill can explain how to inspect a source, but cannot fetch an allowlisted document page, so page access is a bounded tool.

**Skill vs verify_claims tool:** A Skill can remind the model to check citations, but deterministic validation of source IDs and verbatim quotations requires executable code, so it is a tool; semantic support still needs model review.

The Week 15 baseline is commit `0e5f91e7649ba7cf0d1fd3741d16d29f9e99f185` of `baduneev/Engineering_AI_System`. Existing Python files are preserved; Week 16 imports the vector store and reranker lazily and supplies a new CLI.
