from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.deps import get_current_user
from app.rag.retriever import retriever

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=schemas.DocumentOut, status_code=201)
def upload_document(
    payload: schemas.DocumentIn,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Adds a legal source chunk (an Act + Section + text) to the retrieval
    corpus. In production, gate this behind an admin role and pair it with
    a real ingestion pipeline (PDF parsing, chunking) rather than raw text.
    """
    doc = models.LegalDocument(
        act_name=payload.act_name, section=payload.section,
        content=payload.content, category=payload.category,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    retriever.refresh(db)  # keep the in-memory TF-IDF index in sync
    return doc


@router.get("/search", response_model=list[schemas.DocumentOut])
def search_documents(
    q: str = Query(..., min_length=2),
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    chunks = retriever.retrieve(db, q, k=limit, min_score=0.0)
    doc_ids = [c.document_id for c in chunks]
    docs = db.query(models.LegalDocument).filter(models.LegalDocument.id.in_(doc_ids)).all()
    order = {doc_id: i for i, doc_id in enumerate(doc_ids)}
    docs.sort(key=lambda d: order.get(d.id, 999))
    return docs
