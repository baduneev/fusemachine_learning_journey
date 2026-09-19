from pathlib import Path

from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter


CHUNK_SIZE = 800
CHUNK_OVERLAP = 120


def load_pdf(pdf_path: str) -> list[dict]:
    """
    Extract text from a PDF page by page.
    """

    reader = PdfReader(pdf_path)

    pages = []

    for page_number, page in enumerate(
        reader.pages,
        start=1,
    ):
        text = page.extract_text()

        if text and text.strip():
            pages.append(
                {
                    "text": text.strip(),
                    "source": Path(pdf_path).name,
                    "page": page_number,
                }
            )

    return pages


def chunk_pages(pages: list[dict]) -> list[dict]:
    """
    Split extracted pages into smaller overlapping chunks.
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks = []

    for page in pages:

        page_chunks = splitter.split_text(
            page["text"]
        )

        for chunk_index, text in enumerate(
            page_chunks
        ):
            chunks.append(
                {
                    "id": (
                        f"{page['source']}:"
                        f"{page['page']}:"
                        f"{chunk_index}"
                    ),
                    "text": text,
                    "source": page["source"],
                    "page": page["page"],
                }
            )

    return chunks


if __name__ == "__main__":

    pdf_path = "data/documents/sample.pdf"

    pages = load_pdf(pdf_path)
    chunks = chunk_pages(pages)

    print("Pages extracted:", len(pages))
    print("Chunks created:", len(chunks))

    print("\n--- First chunk ---")
    print(chunks[0])