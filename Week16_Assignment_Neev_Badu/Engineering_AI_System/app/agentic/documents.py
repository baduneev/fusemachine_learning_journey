"""Bounded document tools, with lightweight and original W15 retrieval backends."""
from pathlib import Path
import json
import math
import re
from collections import Counter


class Documents:
    def __init__(self, records):
        self.records = records

    @classmethod
    def from_json(cls, path):
        return cls(json.loads(Path(path).read_text(encoding="utf-8")))

    @classmethod
    def from_pdfs(cls, directory):
        from pypdf import PdfReader
        records = []
        for path in sorted(Path(directory).glob("*.pdf")):
            for number, page in enumerate(PdfReader(path).pages, 1):
                text = " ".join((page.extract_text() or "").split())
                # Match W15's 800-character chunks and 120-character overlap.
                for offset in range(0, len(text), 680):
                    records.append({"source": path.name, "page": number, "text": text[offset:offset+800]})
        if not records:
            raise ValueError("No extractable PDF documents were found")
        return cls(records)

    def sources(self):
        return sorted({d["source"] for d in self.records})

    def search(self, query, source=None):
        if source is not None and source not in self.sources():
            raise ValueError("Unknown source")
        terms = set(re.findall(r"\w+", query.lower())) - {"the", "a", "is", "what", "which", "in", "of", "and", "for"}
        scored = []
        for doc in self.records:
            if source and doc["source"] != source:
                continue
            words = Counter(re.findall(r"\w+", doc["text"].lower()))
            score = sum(1 + math.log(words[t]) for t in terms if words[t])
            if score:
                scored.append((score, doc))
        return [d for _, d in sorted(scored, key=lambda pair: -pair[0])[:3]]

    def read(self, source, page):
        # Exact metadata lookup; never accept a model-provided filesystem path.
        found = [d for d in self.records if d["source"] == source and d["page"] == page]
        if not found:
            raise ValueError("Unknown source/page")
        return found[:3]


class W15Documents(Documents):
    """Reuses W15 embeddings, Chroma collection and cross-encoder reranker."""
    def __init__(self, directory):
        super().__init__(Documents.from_pdfs(directory).records)
        from app.rag.vector_store import VectorStore
        from app.rag.reranker import Reranker
        self.store, self.reranker = VectorStore(), Reranker()

    def search(self, query, source=None):
        if source and source not in self.sources():
            raise ValueError("Unknown source")
        count = self.store.collection.count()
        if not count:
            raise ValueError("Build the W15 Chroma index first")
        candidates = self.store.search_candidates(query, top_k=min(10, count))
        candidates = [d for d in candidates if d["distance"] <= 0.67
                      and d["source"] in self.sources() and (not source or d["source"] == source)]
        if not candidates:
            return []
        return self.reranker.rerank(query=query, candidates=candidates, top_n=3)
