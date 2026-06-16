from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.db.session import get_db
from app.models.email_draft import EmailDraft
from app.models.user import User
from app.schemas.email import EmailGeneratedOut, EmailGenerateRequest, EmailHistoryOut
from app.services.ai_service import generate_email_with_ai
from app.main_limiter import limiter

router = APIRouter(prefix="/emails", tags=["Emails"])
settings = get_settings()


@router.post("/generate", response_model=EmailGeneratedOut, status_code=status.HTTP_201_CREATED)
@limiter.limit(settings.rate_limit)
def generate_email(
    request: Request,
    payload: EmailGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = generate_email_with_ai(payload)
    email_draft = EmailDraft(
        user_id=current_user.id,
        purpose=payload.purpose,
        recipient_type=payload.recipient_type,
        tone=payload.tone,
        language=payload.language,
        subject=result.subject,
        body=result.body,
        call_to_action=result.call_to_action,
        score=result.score,
    )
    db.add(email_draft)
    db.commit()
    db.refresh(email_draft)

    return EmailGeneratedOut(
        id=email_draft.id,
        subject=email_draft.subject,
        body=email_draft.body,
        call_to_action=email_draft.call_to_action,
        score=email_draft.score,
        improvement_tips=result.improvement_tips,
    )


@router.get("/history", response_model=list[EmailHistoryOut])
def email_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(EmailDraft)
        .filter(EmailDraft.user_id == current_user.id)
        .order_by(EmailDraft.created_at.desc())
        .limit(50)
        .all()
    )


@router.delete("/{email_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_email(
    email_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    email_draft = (
        db.query(EmailDraft)
        .filter(EmailDraft.id == email_id, EmailDraft.user_id == current_user.id)
        .first()
    )
    if not email_draft:
        raise HTTPException(status_code=404, detail="Email draft not found")
    db.delete(email_draft)
    db.commit()
    return None
