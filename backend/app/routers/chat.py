from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.deps import get_current_user
from app.rag.retriever import retriever
from app.llm.client import complete

router = APIRouter(prefix="/chat", tags=["chat"])

SYSTEM_TEMPLATE = (
    "You are an AI legal assistant for Indian law. Provide informational guidance "
    "only — you are not a lawyer and do not give legal advice. Answer only using the "
    "retrieved context provided below; if it is insufficient to answer confidently, "
    "say so plainly and suggest consulting a licensed advocate. Always cite the Act "
    "and Section you rely on. Never invent or fabricate a law or section that isn't "
    "in the context. Respond in {language}. Keep answers concise and in plain "
    "language. Reply in plain text only, no Markdown syntax.\n\n"
    "RETRIEVED CONTEXT:\n{context}"
)


@router.post("", response_model=schemas.ChatOut)
def send_message(
    payload: schemas.ChatMessageIn,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Find or create the chat
    if payload.chat_id:
        chat = db.query(models.Chat).filter(
            models.Chat.id == payload.chat_id, models.Chat.user_id == current_user.id
        ).first()
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found.")
    else:
        chat = models.Chat(user_id=current_user.id, title=payload.message[:60])
        db.add(chat)
        db.commit()
        db.refresh(chat)

    # Save the user's message
    user_msg = models.Message(chat_id=chat.id, role="user", content=payload.message, sources=[])
    db.add(user_msg)
    db.commit()

    # Retrieve context and log the search
    chunks = retriever.retrieve(db, payload.message, k=3)
    db.add(models.SearchHistory(user_id=current_user.id, query=payload.message, result_count=len(chunks)))
    db.commit()

    context_block = "\n\n".join(f"[{c.act_name} — {c.section}] {c.text}" for c in chunks) or "(no relevant sources found)"
    system_prompt = SYSTEM_TEMPLATE.format(language=payload.language or "English", context=context_block)

    answer = complete(system_prompt, payload.message)

    sources_json = [{"act_name": c.act_name, "section": c.section, "text": c.text} for c in chunks]
    assistant_msg = models.Message(chat_id=chat.id, role="assistant", content=answer, sources=sources_json)
    db.add(assistant_msg)
    db.commit()
    db.refresh(chat)

    return chat


@router.get("/{chat_id}", response_model=schemas.ChatOut)
def get_chat(
    chat_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    chat = db.query(models.Chat).filter(
        models.Chat.id == chat_id, models.Chat.user_id == current_user.id
    ).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found.")
    return chat


@router.get("", response_model=list[schemas.ChatSummaryOut])
def list_chats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return db.query(models.Chat).filter(models.Chat.user_id == current_user.id).order_by(models.Chat.created_at.desc()).all()
