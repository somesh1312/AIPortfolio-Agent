import sys
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

# Base dir = project root (AIPortfolioAgent)
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR / "backend"))  # 👈 add backend to sys.path

from backend.loader import load_markdown_docs  # ✅ now Python can find loader.py

STORAGE = BASE_DIR / "storage"
STORAGE.mkdir(exist_ok=True)

# ✅ Load .env from project root
load_dotenv(BASE_DIR / ".env")

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("❌ OPENAI_API_KEY not found. Please check your .env file.")

# ✅ Use smaller embedding model (cheaper & quota friendly)
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    openai_api_key=api_key
)

# ✅ Define text splitter
splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=50
)

print("📂 Loading markdown docs...")
docs = load_markdown_docs()
print(f"✅ Loaded {len(docs)} documents")

if not docs:
    print("⚠️ No markdown files found in backend/content/. Add some .md files before building the index.")
    exit()

print("✂️ Splitting into chunks...")
all_chunks = []
for doc in docs:
    chunks = splitter.split_documents([doc])
    if chunks:
        all_chunks.extend(chunks)
    else:
        # Fallback if doc is very short
        all_chunks.append(doc)

print(f"✅ Created {len(all_chunks)} chunks")

print("⚡ Building FAISS index...")
vs = FAISS.from_documents(all_chunks, embeddings)
vs.save_local(str(STORAGE / "faiss_index"))
print("✅ Index saved to storage/faiss_index")