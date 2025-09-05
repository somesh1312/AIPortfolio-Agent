import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
from backend.rag_utils import load_vectorstore, answer_question

load_dotenv()
API = FastAPI(title="Somesh Portfolio Agent API")

# Allow frontend
origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

API.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Serve resumes (PDFs in backend/resumes)
API.mount("/resumes", StaticFiles(directory="resumes"), name="resumes")

# Load FAISS vectorstore
VECTORSTORE = load_vectorstore()

class ChatRequest(BaseModel):
    message: str

@API.get("/")
def root():
    return {"message": "AI Portfolio Agent is live 🚀"}

@API.get("/api/health")
def health():
    return {"ok": True}

@API.post("/api/chat")
def chat(req: ChatRequest):
    # detect your domain dynamically (Railway injects it in request)
    public_domain = os.getenv("PUBLIC_DOMAIN", "http://localhost:8000")

    resumes = [
        {
            "label": "Cloud Engineer",
            "url": f"{public_domain}/resumes/Somesh-Cloud-Engineer.pdf",
        },
        {
            "label": "Data/Analytics",
            "url": f"{public_domain}/resumes/somesh-data-analytics.pdf",
        },
    ]

    canon = {
        "email": os.getenv("SOMESH_EMAIL", "hidden@example.com"),
        "phone": os.getenv("SOMESH_PHONE", "+1-000-000-0000"),
        "resumes": resumes,
        "schedule": os.getenv("CALENDLY_URL", "https://calendly.com/somesh1st/30min"),
    }

    out = answer_question(VECTORSTORE, req.message, canon)
    return out


if __name__ == "__main__":
    import uvicorn
    # ✅ Use Railway's PORT if available
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(API, host="0.0.0.0", port=port)