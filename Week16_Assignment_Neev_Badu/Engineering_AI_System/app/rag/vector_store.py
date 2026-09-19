import chromadb

from app.rag.embedder import Embedder
from app.rag.ingest import load_pdf, chunk_pages


CHROMA_PATH = "data/chroma_db"
COLLECTION_NAME = "technical_documents"


class VectorStore:

    def __init__(self):

        self.client = chromadb.PersistentClient(
            path=CHROMA_PATH
        )

        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

        self.embedder = Embedder()


    def add_chunks(self, chunks: list[dict]) -> None:

        texts = [
            chunk["text"]
            for chunk in chunks
        ]

        embeddings = self.embedder.embed_documents(texts)

        ids = [
            str(chunk["id"])
            for chunk in chunks
        ]

        metadatas = [
            {
                "source": chunk["source"],
                "page": chunk["page"],
            }
            for chunk in chunks
        ]

        self.collection.upsert(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
        )


    def search(
        self,
        query: str,
        top_k: int = 3,
    ) -> dict:

        query_embedding = self.embedder.embed_query(query)

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )

        return results


    def search_candidates(
        self,
        query: str,
        top_k: int = 10,
    ) -> list[dict]:
        """
        Retrieve candidate chunks in a clean format
        for second-stage reranking.
        """

        results = self.search(
            query=query,
            top_k=top_k,
        )

        candidates = []

        for document, metadata, distance in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):

            candidates.append(
                {
                    "text": document,
                    "source": metadata["source"],
                    "page": metadata["page"],
                    "distance": float(distance),
                }
            )

        return candidates


if __name__ == "__main__":

    pdf_path = "data/documents/sample.pdf"

    pages = load_pdf(pdf_path)
    chunks = chunk_pages(pages)

    vector_store = VectorStore()

    vector_store.add_chunks(chunks)

    print(
        f"Stored {len(chunks)} chunks in ChromaDB."
    )

    query = "Which framework is used for browser automation?"

    results = vector_store.search(
        query=query,
        top_k=3,
    )

    print("\nQuery:", query)

    for i in range(len(results["documents"][0])):

        print(f"\n--- Result {i + 1} ---")

        print(
            "Source:",
            results["metadatas"][0][i]["source"]
        )

        print(
            "Page:",
            results["metadatas"][0][i]["page"]
        )

        print(
            "Distance:",
            results["distances"][0][i]
        )

        print(
            "Text:",
            results["documents"][0][i]
        )