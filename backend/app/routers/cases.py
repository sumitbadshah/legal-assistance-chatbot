from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.deps import get_current_user

router = APIRouter(prefix="/cases", tags=["cases"])


@router.get("/search", response_model=list[schemas.CaseOut])
def search_cases(
    q: str = Query(..., min_length=2),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    like = f"%{q}%"
    return (
        db.query(models.Case)
        .filter(
            (models.Case.title.ilike(like))
            | (models.Case.summary.ilike(like))
            | (models.Case.citation.ilike(like))
        )
        .limit(20)
        .all()
    )
