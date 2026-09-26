import argparse
import json
from pathlib import Path
from app.agentic.core import Agent
from app.agentic.documents import Documents, W15Documents
from app.agentic.providers import GeminiModel


def main():
    parser = argparse.ArgumentParser(description="Week 16 evidence-checking assistant")
    parser.add_argument("question")
    parser.add_argument("--backend", choices=["pdf", "chroma"], default="pdf")
    parser.add_argument("--documents", default="data/documents")
    parser.add_argument("--model", help="Gemini model ID available to your account")
    parser.add_argument("--max-steps", type=int, default=8)
    parser.add_argument("--inject-failure", choices=["search_unavailable", "malformed_once"])
    parser.add_argument("--output", default="runs/latest.json")
    args = parser.parse_args()
    try:
        model = GeminiModel(args.model)
        documents = (W15Documents(args.documents) if args.backend == "chroma"
                     else Documents.from_pdfs(args.documents))
        result = Agent(model, documents, args.max_steps, args.inject_failure).run(args.question)
    except ValueError as exc:
        parser.error(str(exc))
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_dict(), indent=2), encoding="utf-8")
    print(f"Status: {result.status}\n{result.answer}")
    for claim in result.claims:
        evidence = result.evidence[claim["source_id"]]
        print(f"  [{claim['source_id']}] {evidence['source']}, page {evidence['page']}")
    print(f"Iterations: {len(result.trajectory)} | Tokens: {result.usage['total_tokens']}")
    print(f"Trace saved: {path}")
    if result.status in {"error", "max_steps"}:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
