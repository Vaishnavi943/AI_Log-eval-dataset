from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import EvalCase, ReviewEvent, DatasetStatus, Log
from app.schemas import ReviewAction, EvalCaseOut

router = APIRouter(prefix="/review", tags=["review"])

LOW_CONFIDENCE_THRESHOLD = 0.7


@router.get("/queue", response_model=list[EvalCaseOut])
def get_review_queue(limit: int = 20, db: Session = Depends(get_db)):
    """Low-confidence, still-draft eval cases, lowest confidence first."""
    return (
        db.query(EvalCase)
        .filter(EvalCase.status == DatasetStatus.draft)
        .filter(EvalCase.confidence < LOW_CONFIDENCE_THRESHOLD)
        .order_by(EvalCase.confidence.asc())
        .limit(limit)
        .all()
    )


@router.get("/queue/{case_id}/context")
def get_case_context(case_id: str, db: Session = Depends(get_db)):
    """Original interaction + similar existing approved cases, for reviewer context."""
    case = db.query(EvalCase).filter(EvalCase.id == case_id).first()
    if not case:
        raise HTTPException(404, "case not found")
    log = db.query(Log).filter(Log.id == case.source_log_id).first() if case.source_log_id else None
    similar = []
    if case.source_cluster_id:
        similar = (
            db.query(EvalCase)
            .filter(EvalCase.source_cluster_id == case.source_cluster_id)
            .filter(EvalCase.status == DatasetStatus.approved)
            .limit(5)
            .all()
        )
    return {
        "case": EvalCaseOut.model_validate(case),
        "original_log": {"prompt": log.prompt, "response": log.response} if log else None,
        "similar_approved_cases": [EvalCaseOut.model_validate(s) for s in similar],
    }


@router.post("/queue/{case_id}/action", response_model=EvalCaseOut)
def review_action(case_id: str, action: ReviewAction, db: Session = Depends(get_db)):
    case = db.query(EvalCase).filter(EvalCase.id == case_id).first()
    if not case:
        raise HTTPException(404, "case not found")

    diff = {}
    if action.action == "approve":
        case.status = DatasetStatus.approved
    elif action.action == "reject":
        case.status = DatasetStatus.rejected
        case.rejected_reason = action.reason
    elif action.action == "edit":
        if action.edits:
            for field, value in action.edits.items():
                if hasattr(case, field):
                    diff[field] = {"old": getattr(case, field), "new": value}
                    setattr(case, field, value)
        case.status = DatasetStatus.approved
        case.auto_labeled = False
    else:
        raise HTTPException(400, "action must be approve, edit, or reject")

    event = ReviewEvent(
        eval_case_id=case.id,
        action=action.action,
        reviewer=action.reviewer,
        diff=diff or None,
        reason=action.reason,
    )
    db.add(event)
    db.commit()
    db.refresh(case)
    return case
