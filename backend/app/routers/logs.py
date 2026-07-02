from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Log
from app.schemas import LogOut, SeedRequest, LogCreate
from app.services.seed import generate_synthetic_logs
from app.services.privacy import redact, REDACTION_METHOD

router = APIRouter(prefix="/logs", tags=["logs"])


@router.post("/seed")
def seed_logs(req: SeedRequest, db: Session = Depends(get_db)):
    logs = generate_synthetic_logs(req.count)
    db.bulk_save_objects(logs)
    db.commit()
    return {"created": len(logs)}


@router.post("", response_model=LogOut)
def create_log(payload: LogCreate, db: Session = Depends(get_db)):
    """Manually add a single log — same redaction pipeline as seeded/ingested logs."""
    redacted_prompt, fields, was_redacted = redact(payload.prompt)
    log = Log(
        prompt=redacted_prompt,
        system_prompt=payload.system_prompt,
        response=payload.response,
        model=payload.model,
        feature_name=payload.feature_name,
        user_feedback=payload.user_feedback,
        error_status=payload.error_status,
        retry_count=payload.retry_count,
        is_redacted=was_redacted,
        redaction_method=REDACTION_METHOD if was_redacted else None,
        redacted_fields=fields,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router.get("", response_model=list[LogOut])
def list_logs(
    feature_name: str | None = None,
    error_status: str | None = None,
    user_feedback: str | None = None,
    cluster_id: str | None = None,
    limit: int = Query(50, le=500),
    offset: int = 0,
    db: Session = Depends(get_db),
):
    q = db.query(Log)
    if feature_name:
        q = q.filter(Log.feature_name == feature_name)
    if error_status:
        q = q.filter(Log.error_status == error_status)
    if user_feedback:
        q = q.filter(Log.user_feedback == user_feedback)
    if cluster_id:
        q = q.filter(Log.cluster_id == cluster_id)
    return q.order_by(Log.created_at.desc()).offset(offset).limit(limit).all()


@router.get("/{log_id}", response_model=LogOut)
def get_log(log_id: str, db: Session = Depends(get_db)):
    return db.query(Log).filter(Log.id == log_id).first()


@router.get("/stats/summary")
def log_stats(db: Session = Depends(get_db)):
    total = db.query(Log).count()
    redacted = db.query(Log).filter(Log.is_redacted.is_(True)).count()
    errors = db.query(Log).filter(Log.error_status.isnot(None)).count()
    negative = db.query(Log).filter(Log.user_feedback == "negative").count()
    return {
        "total_logs": total,
        "redacted_logs": redacted,
        "error_logs": errors,
        "negative_feedback_logs": negative,
    }
