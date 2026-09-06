import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, Text, DateTime, ForeignKey, Integer, JSON, Boolean, Float
)
from sqlalchemy.orm import relationship

from app.database import Base


def gen_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    preferred_language = Column(String, default="English")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    chats = relationship("Chat", back_populates="user", cascade="all, delete-orphan")
    generated_documents = relationship("GeneratedDocument", back_populates="user", cascade="all, delete-orphan")
    feedback_entries = relationship("Feedback", back_populates="user", cascade="all, delete-orphan")
    search_history = relationship("SearchHistory", back_populates="user", cascade="all, delete-orphan")


class Chat(Base):
    __tablename__ = "chats"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    title = Column(String, default="New conversation")
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="chats")
    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan", order_by="Message.created_at")


class Message(Base):
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    chat_id = Column(String(36), ForeignKey("chats.id"), nullable=False)
    role = Column(String, nullable=False)  # "user" | "assistant"
    content = Column(Text, nullable=False)
    sources = Column(JSON, default=list)  # list of {act, section, text}
    created_at = Column(DateTime, default=datetime.utcnow)

    chat = relationship("Chat", back_populates="messages")
    feedback_entries = relationship("Feedback", back_populates="message", cascade="all, delete-orphan")


class LegalDocument(Base):
    """A chunk of legal source text (an Act/Section) used for RAG retrieval."""
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    act_name = Column(String, nullable=False)
    section = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String, nullable=True)  # e.g. "constitutional", "criminal", "consumer"
    created_at = Column(DateTime, default=datetime.utcnow)

    embedding = relationship("Embedding", back_populates="document", uselist=False, cascade="all, delete-orphan")


class Embedding(Base):
    """Vector representation of a document chunk. Stored as JSON floats for
    portability; swap to pgvector's `vector` type in production for ANN search."""
    __tablename__ = "embeddings"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    document_id = Column(String(36), ForeignKey("documents.id"), nullable=False, unique=True)
    vector = Column(JSON, nullable=False)  # list[float]
    model_name = Column(String, default="tfidf-v1")

    document = relationship("LegalDocument", back_populates="embedding")


class Case(Base):
    __tablename__ = "cases"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    title = Column(String, nullable=False)
    court = Column(String, nullable=True)
    judge = Column(String, nullable=True)
    year = Column(Integer, nullable=True)
    citation = Column(String, nullable=True)
    summary = Column(Text, nullable=True)
    related_acts = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)


class GeneratedDocument(Base):
    __tablename__ = "generated_documents"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    doc_type = Column(String, nullable=False)  # e.g. "affidavit", or free-text type
    input_fields = Column(JSON, default=dict)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="generated_documents")


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    message_id = Column(String(36), ForeignKey("messages.id"), nullable=True)
    rating = Column(String, nullable=False)  # "up" | "down"
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="feedback_entries")
    message = relationship("Message", back_populates="feedback_entries")


class SearchHistory(Base):
    __tablename__ = "search_history"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    query = Column(String, nullable=False)
    result_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="search_history")
