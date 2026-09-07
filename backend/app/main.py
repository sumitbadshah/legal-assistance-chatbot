from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import Base, engine, SessionLocal
from app.routers import auth, chat, documents, draft, feedback, cases
from app.seed_data import seed_if_empty
from app.rag.retriever import retriever

settings = get_settings()

app = FastAPI(
    title="AI Legal Assistance API",
    description="Backend for the AI-powered legal information chatbot: RAG-grounded Q&A, "
                "document drafting, case search, and legal aid info — informational use only, "
                "not a substitute for a licensed advocate.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(documents.router)
app.include_router(draft.router)
app.include_router(feedback.router)
app.include_router(cases.router)


@app.on_event("startup")
def on_startup():
    # Creates tables if they don't exist. For schema changes after go-live,
    # switch to Alembic migrations instead of relying on create_all.
    Base.metadata.create_all(bind=engine)
    print("ALLOWED ORIGINS:", settings.cors_origins)  
    db = SessionLocal()
    try:
        seed_if_empty(db)
        retriever.refresh(db)
    finally:
        db.close()


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}
