"""
Lightweight RAG retriever.

For an MVP that deploys anywhere without a separate embeddings API or a
GPU, this uses scikit-learn TF-IDF + cosine similarity over the `documents`
table. It rebuilds its in-memory index from the DB (cheap at this corpus
size) whenever `refresh()` is called or the index hasn't been built yet.

For production scale, swap this for:
- pgvector column on `embeddings.vector` with real embedding model, or
- a dedicated vector DB (Chroma / Pinecone / FAISS service) as sketched
  in SYSTEM_ARCHITECTURE.md, queried via approximate nearest neighbour.
The public interface (`retrieve(query, k)`) would stay the same, so
callers (chat/draft routers) would not need to change.
"""
from __future__ import annotations
from dataclasses import dataclass
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.orm import Session

from app import models


@dataclass
class RetrievedChunk:
    document_id: str
    act_name: str
    section: str
    text: str
    score: float


class Retriever:
    def __init__(self):
        self._vectorizer: TfidfVectorizer | None = None
        self._matrix = None
        self._docs: list[models.LegalDocument] = []

    def refresh(self, db: Session):
        self._docs = db.query(models.LegalDocument).all()
        corpus = [f"{d.act_name} {d.section} {d.content}" for d in self._docs]
        if not corpus:
            self._vectorizer = None
            self._matrix = None
            return
        self._vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        self._matrix = self._vectorizer.fit_transform(corpus)

    def is_ready(self) -> bool:
        return self._vectorizer is not None and self._matrix is not None

    def retrieve(self, db: Session, query: str, k: int = 3, min_score: float = 0.05) -> list[RetrievedChunk]:
        if not self.is_ready():
            self.refresh(db)
        if not self.is_ready():
            return []

        query_vec = self._vectorizer.transform([query])
        sims = cosine_similarity(query_vec, self._matrix).flatten()
        ranked_idx = sims.argsort()[::-1][:k]

        results = []
        for idx in ranked_idx:
            score = float(sims[idx])
            if score < min_score:
                continue
            doc = self._docs[idx]
            results.append(RetrievedChunk(
                document_id=doc.id, act_name=doc.act_name,
                section=doc.section, text=doc.content, score=score,
            ))
        return results


# Module-level singleton — fine for a single-process deployment.
# Behind multiple workers, each worker builds its own copy (cheap at this
# corpus size); for large corpora, precompute and persist instead.
retriever = Retriever()
