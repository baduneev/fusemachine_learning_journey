from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class Embedder:
    def __init__(self):
        self.model = SentenceTransformer(MODEL_NAME)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """
        Convert multiple document chunks into embedding vectors.
        """

        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
        )

        return embeddings.tolist()

    def embed_query(self, query: str) -> list[float]:
        """
        Convert one user query into an embedding vector.
        """

        embedding = self.model.encode(
            query,
            normalize_embeddings=True,
        )

        return embedding.tolist()


if __name__ == "__main__":

    embedder = Embedder()

    text = "The QA agent executes browser tests using Playwright."

    vector = embedder.embed_query(text)

    print("Embedding dimensions:", len(vector))
    print("First 10 values:")
    print(vector[:10])
