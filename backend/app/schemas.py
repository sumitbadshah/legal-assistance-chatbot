from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, EmailStr


# ---- Auth ----
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    email: EmailStr
    full_name: Optional[str]
    preferred_language: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ---- Chat ----
class ChatMessageIn(BaseModel):
    chat_id: Optional[str] = None  # omit to start a new chat
    message: str
    language: Optional[str] = "English"


class SourceOut(BaseModel):
    act_name: str
    section: str
    text: str


class MessageOut(BaseModel):
    id: str
    role: str
    content: str
    sources: list[dict] = []
    created_at: datetime

    class Config:
        from_attributes = True


class ChatOut(BaseModel):
    id: str
    title: str
    created_at: datetime
    messages: list[MessageOut] = []

    class Config:
        from_attributes = True


class ChatSummaryOut(BaseModel):
    id: str
    title: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---- Documents (legal source corpus) ----
class DocumentIn(BaseModel):
    act_name: str
    section: str
    content: str
    category: Optional[str] = None


class DocumentOut(BaseModel):
    id: str
    act_name: str
    section: str
    content: str
    category: Optional[str]

    class Config:
        from_attributes = True


# ---- Drafting ----
class DraftRequest(BaseModel):
    doc_type: str  # e.g. "Affidavit", or any free-text description
    fields: dict[str, Any] = {}
    language: Optional[str] = "English"


class DraftOut(BaseModel):
    id: str
    doc_type: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---- Feedback ----
class FeedbackIn(BaseModel):
    message_id: Optional[str] = None
    rating: str  # "up" | "down"
    comment: Optional[str] = None


# ---- Cases ----
class CaseOut(BaseModel):
    id: str
    title: str
    court: Optional[str]
    judge: Optional[str]
    year: Optional[int]
    citation: Optional[str]
    summary: Optional[str]
    related_acts: list[str] = []

    class Config:
        from_attributes = True
