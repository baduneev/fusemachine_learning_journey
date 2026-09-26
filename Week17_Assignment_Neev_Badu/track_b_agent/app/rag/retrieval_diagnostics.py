from app.rag.vector_store import VectorStore


vector_store = VectorStore()

query = "What happens when deterministic matching fails?"

results = vector_store.search(
    query=query,
    top_k=10,
)

print("\nQuestion:")
print(query)

for i in range(len(results["documents"][0])):
    print(f"\n--- Result {i + 1} ---")

    print(
        "Distance:",
        round(results["distances"][0][i], 4)
    )

    print(
        "Page:",
        results["metadatas"][0][i]["page"]
    )

    print(
        "Text:",
        results["documents"][0][i][:500]
    )