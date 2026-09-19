import os
from app.rag.reranker import Reranker
from dotenv import load_dotenv
from google import genai


from app.rag.vector_store import VectorStore
from app.schemas import RAGResponse

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY was not found in the .env file.")


client = genai.Client(api_key=api_key)


RAG_SYSTEM_PROMPT = """
You are a document-grounded technical assistant.

Rules:
- Answer using ONLY the retrieved context provided to you.
- Do not use outside knowledge to fill missing information.
- If the retrieved context does not contain enough information, clearly say that the answer is not available in the provided documents.
- Cite only source IDs that actually support the answer.
- Do not invent source IDs.
- Be concise and technically accurate.
"""
RETRIEVAL_DISTANCE_THRESHOLD = 0.67


def retrieve_context(
    vector_store: VectorStore,
    reranker: Reranker,
    question: str,
    candidate_k: int = 10,
    final_k: int = 3,
):
    """
    Retrieve candidate chunks using embeddings,
    then rerank them using a cross-encoder.
    """

    # Stage 1: fast embedding retrieval
    candidates = vector_store.search_candidates(
        query=question,
        top_k=candidate_k,
    )

    if not candidates:
        return "", {}, float("inf")

    # Best embedding distance is used for rejection
    best_distance = min(candidate["distance"] for candidate in candidates)

    # Stage 2: more accurate cross-encoder reranking
    ranked_candidates = reranker.rerank(
        query=question,
        candidates=candidates,
        top_n=final_k,
    )

    print("\n[Retrieval] Reranked evidence:")

    for i, candidate in enumerate(
        ranked_candidates,
        start=1,
    ):
        print(
            f"  {i}. page={candidate['page']}, "
            f"distance={candidate['distance']:.4f}, "
            f"rerank={candidate['rerank_score']:.4f}"
        )

    context_blocks = []
    source_map = {}

    for index, candidate in enumerate(
        ranked_candidates,
        start=1,
    ):
        source_id = f"S{index}"

        source_map[source_id] = {
            "source": candidate["source"],
            "page": candidate["page"],
            "distance": candidate["distance"],
            "rerank_score": candidate["rerank_score"],
            "text": candidate["text"],
        }

        context_blocks.append(f"""
[{source_id}]
Source: {candidate["source"]}
Page: {candidate["page"]}
Content:
{candidate["text"]}
""".strip())

    context = "\n\n".join(context_blocks)

    return context, source_map, best_distance


def answer_question(
    question: str,
    top_k: int = 3,
):
    print("[1] Creating vector store...")
    vector_store = VectorStore()
    reranker = Reranker()

    print("[2] Retrieving chunks...")
    context, source_map, best_distance = retrieve_context(
        vector_store=vector_store,
        reranker=reranker,
        question=question,
        candidate_k=10,
        final_k=top_k,
    )
    print("[3] Retrieval complete.")
    print(f"[3.5] Best retrieval distance: " f"{best_distance:.4f}")

    if best_distance > RETRIEVAL_DISTANCE_THRESHOLD:

        print("[3.6] Retrieval rejected: " "evidence is too weak.")

        response = RAGResponse(
            answer=(
                "The available documents do not contain "
                "sufficiently relevant information to answer "
                "this question."
            ),
            source_ids=[],
            confidence=0.0,
        )

        return response, []

    prompt = f"""
USER QUESTION:
{question}

RETRIEVED CONTEXT:
{context}

Answer the user question using only the retrieved context.
"""

    print("[4] Sending request to Gemini...")

    interaction = client.interactions.create(
        model="gemini-3.6-flash",
        system_instruction=RAG_SYSTEM_PROMPT,
        input=prompt,
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": RAGResponse.model_json_schema(),
        },
    )

    print("[5] Gemini response received.")

    response = RAGResponse.model_validate_json(interaction.output_text)

    used_sources = []

    for source_id in response.source_ids:
        if source_id in source_map:
            used_sources.append(
                {
                    "source_id": source_id,
                    **source_map[source_id],
                }
            )

    return response, used_sources


if __name__ == "__main__":

    question = "Which framework is used for browser automation?"

    response, sources = answer_question(question)

    print("\nQuestion:")
    print(question)

    print("\nAnswer:")
    print(response.answer)

    print("\nConfidence:")
    print(response.confidence)

    print("\nSources:")

    for source in sources:
        print(f"- {source['source_id']}: " f"{source['source']}, page {source['page']}")
