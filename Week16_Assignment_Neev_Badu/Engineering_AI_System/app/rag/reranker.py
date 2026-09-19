from sentence_transformers import CrossEncoder


RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"


class Reranker:

    def __init__(self):
        self.model = CrossEncoder(RERANKER_MODEL)


    def rerank(
        self,
        query: str,
        candidates: list[dict],
        top_n: int = 3,
    ) -> list[dict]:
        """
        Rerank retrieved chunks according to their
        relevance to the user's query.
        """

        pairs = [
            [query, candidate["text"]]
            for candidate in candidates
        ]

        scores = self.model.predict(pairs)

        for candidate, score in zip(candidates, scores):
            candidate["rerank_score"] = float(score)

        ranked = sorted(
            candidates,
            key=lambda item: item["rerank_score"],
            reverse=True,
        )

        return ranked[:top_n]
    
    
if __name__ == "__main__":

    from app.rag.vector_store import VectorStore

    question = (
        "What happens when deterministic matching fails?"
    )

    vector_store = VectorStore()

    candidates = vector_store.search_candidates(
        query=question,
        top_k=10,
    )

    reranker = Reranker()

    ranked = reranker.rerank(
        query=question,
        candidates=candidates,
        top_n=5,
    )

    print("\nQuestion:")
    print(question)

    for i, item in enumerate(ranked, start=1):

        print(f"\n--- Reranked Result {i} ---")

        print(
            "Original distance:",
            round(item["distance"], 4)
        )

        print(
            "Reranker score:",
            round(item["rerank_score"], 4)
        )

        print("Page:", item["page"])

        print(
            "Text:",
            item["text"][:500]
        )