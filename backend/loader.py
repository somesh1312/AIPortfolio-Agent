from pathlib import Path
from langchain_core.documents import Document

CONTENT_DIR = Path(__file__).parent / "content"

def load_markdown_docs() -> list[Document]:
    docs: list[Document] = []
    for path in CONTENT_DIR.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        print(f"📄 Loaded {path.name}, length={len(text)} chars")  # <-- ADD THIS
        docs.append(Document(
            page_content=text,
            metadata={"source": str(path.relative_to(CONTENT_DIR))}
        ))
    return docs