from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.deps import get_current_user

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("", status_code=status.HTTP_201_CREATED)
def submit_feedback(
    payload: schemas.FeedbackIn,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    entry = models.Feedback(
        user_id=current_user.id, message_id=payload.message_id,
        rating=payload.rating, comment=payload.comment,
    )
    db.add(entry)
    db.commit()
    return {"status": "recorded"}
