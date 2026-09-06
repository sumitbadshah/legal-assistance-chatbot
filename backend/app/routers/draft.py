from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.deps import get_current_user
from app.llm.client import complete

router = APIRouter(prefix="/draft", tags=["draft"])

SYSTEM_TEMPLATE = (
    "You are a legal document drafting assistant for India. Draft a professional, "
    "standard-form '{doc_type}' using Indian legal drafting conventions (headers, "
    "recitals/clauses, signature and witness blocks as appropriate for this document "
    "type). This is a template for informational use only. At the very top, include "
    "the line: \"DRAFT — for reference only. Have this reviewed by a licensed "
    "advocate before signing or filing.\" If the requested document type is unclear "
    "or not a real legal instrument, say so instead of guessing. Respond in "
    "{language}. Format as plain text only, no Markdown syntax — use plain "
    "capitalized headings, numbered clauses, and blank lines for structure."
)


@router.post("/generate", response_model=schemas.DraftOut, status_code=201)
def generate_draft(
    payload: schemas.DraftRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    detail_lines = "\n".join(f"{k}: {v}" for k, v in payload.fields.items()) or "(no additional details provided)"
    system_prompt = SYSTEM_TEMPLATE.format(doc_type=payload.doc_type, language=payload.language or "English")
    user_prompt = f"Document requested: {payload.doc_type}\n\nDetails supplied:\n{detail_lines}"

    content = complete(system_prompt, user_prompt, max_tokens=1500)

    record = models.GeneratedDocument(
        user_id=current_user.id, doc_type=payload.doc_type,
        input_fields=payload.fields, content=content,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/history", response_model=list[schemas.DraftOut])
def draft_history(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return (
        db.query(models.GeneratedDocument)
        .filter(models.GeneratedDocument.user_id == current_user.id)
        .order_by(models.GeneratedDocument.created_at.desc())
        .all()
    )
