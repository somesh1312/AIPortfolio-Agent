from typing import Dict, Any
from pathlib import Path
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate

BASE = Path(__file__).parent
load_dotenv(BASE / ".env")   # load .env variables

SYSTEM_PROMPT = """
You are Somesh’s AI Portfolio Agent.

Special rules:
- If the user asks about resumes, DO NOT generate fake URLs or Markdown links.
- Instead, say something like: "Here’s Somesh’s Cloud Engineer resume — you can download it below 👇. If you’d also like his Data/Analytics resume, just let me know!"
- The actual links will always come from canonical data (resumes list). Let the frontend render them as buttons.
- For scheduling, say: "You can book a call with Somesh below 👇" and let the frontend show the Calendly button.
- If the info isn’t in context, say: "I don’t have that information yet."
- Never say "I don’t have that information yet" if the relevant file exists.

Rules:
- If the user asks about certifications, always pull from certs.md.
- If the user asks what Somesh is doing right now, always pull from now.md.
- If the user asks for contact details, always pull from contact.md.

Guidelines:
- Be natural, fluid, and conversational.
- Use sentences and short paragraphs instead of Markdown-heavy bullets.
- Only use lists if the user specifically asks (e.g., "list certifications").
- When asked "Who is Somesh?", give a warm, polished introduction in 3–5 sentences.
- When asked about projects, summarize clearly but avoid placeholders.
- Always keep the tone professional yet approachable.
- Never use Markdown headers (###) or heavy formatting. 
- Reply in plain conversational text, with occasional short lists only if absolutely necessary.

Tone:
- Professional yet approachable.
- Confident, like a candidate introduction at a top interview.
- Always frame Somesh as skilled, proactive, and impact-driven.
"""

PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("user", "Question: {question}\n\nContext:\n{context}\n\nCanonical:\nemail={email}\nphone={phone}\nresumes={resumes}\nschedule={schedule}")
])


def load_vectorstore() -> FAISS:
    """Load FAISS index from disk with OpenAI embeddings."""
    storage = BASE / "storage" / "faiss_index"
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Missing OPENAI_API_KEY in environment")
    vs = FAISS.load_local(
        str(storage),
        OpenAIEmbeddings(openai_api_key=api_key),
        allow_dangerous_deserialization=True
    )
    return vs


def format_docs(docs) -> str:
    """Format retrieved documents into a string context."""
    blocks = []
    for i, d in enumerate(docs, start=1):
        src = d.metadata.get("source", "unknown")
        blocks.append(f"[{i}] {src}\n{d.page_content.strip()[:500]}")
    return "\n\n".join(blocks)


def answer_question(vs: FAISS, question: str, canon: Dict[str, Any]) -> Dict[str, Any]:
    """Answer a user question using RAG and canonical data."""
    retriever = vs.as_retriever(search_type="similarity", search_kwargs={"k": 8})
    q_lower = question.lower()

    # ✅ Special hard overrides
    if "resume" in q_lower:
        return {
            "answer": "Here’s Somesh’s Cloud Engineer resume — you can download it below 👇. If you’d also like his Data/Analytics resume, just let me know!",
            "sources": [],
            "resumes": canon["resumes"],
            "schedule": canon["schedule"],
        }

    if "schedule" in q_lower or "book a call" in q_lower or "meeting" in q_lower:
        return {
            "answer": "You can book a call with Somesh below 👇",
            "sources": [],
            "resumes": canon["resumes"],
            "schedule": canon["schedule"],
        }

    # ✅ Bias retrieval for specific docs
    if "certification" in q_lower or "certifications" in q_lower:
        docs = retriever.invoke("certifications")
        docs = [d for d in docs if "certs.md" in d.metadata.get("source", "")] or docs
    elif "contact" in q_lower or "email" in q_lower or "phone" in q_lower:
        docs = retriever.invoke("contact information")
        docs = [d for d in docs if "contact.md" in d.metadata.get("source", "")] or docs
    elif "doing right now" in q_lower or "current" in q_lower or "now" in q_lower:
        docs = retriever.invoke("current activities")
        docs = [d for d in docs if "now.md" in d.metadata.get("source", "")] or docs
    else:
        docs = retriever.invoke(question)

    context = format_docs(docs)

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        api_key=os.getenv("OPENAI_API_KEY")
    )

    msg = PROMPT.format(
        question=question,
        context=context,
        email=canon["email"],
        phone=canon["phone"],
        resumes="\n".join([f"{r['label']}: {r['url']}" for r in canon["resumes"]]),
        schedule=canon["schedule"],
    )
    resp = llm.invoke(msg)

    return {
        "answer": resp.content,
        "sources": sorted({d.metadata.get("source", "unknown") for d in docs}),
        "resumes": canon["resumes"],
        "schedule": canon["schedule"],
    }