from __future__ import annotations
from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app import models


def get_current_user(
    db: Session = Depends(get_db),
) -> models.User:
    user = db.query(models.User).filter(models.User.email == "demo@example.com").first()
    if not user:
        user = models.User(email="demo@example.com", hashed_password="dummy")
        db.add(user)
        db.commit()
        db.refresh(user)
    return user
