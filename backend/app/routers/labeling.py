from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Log, EvalCase, DatasetStatus
from app.schemas import LabelRequest, EvalCaseOut
from app.services.labeling import label_log
from app.services.dedup import is_duplicate, text_hash

router = APIRouter(prefix="/labeling", tags=["labeling"])

LOW_CONFIDENCE_THRESHOLD = 0.7


@router.get("/candidates", response_model=list)
def get_candidates(limit: int = 30, db: Session = Depends(get_db)):
    """Phase 2.3: prioritize unusual prompts, low-quality outputs, edge cases,
    and clusters with poor eval coverage."""
    from sqlalchemy import or_
    q = db.query(Log).filter(
        or_(
            Log.user_feedback == "negative",
            Log.error_status.isnot(None),
            Log.retry_count > 0,
        )
    ).limit(limit).all()
    if len(q) < limit:
        extra = db.query(Log).order_by(Log.created_at.desc()).limit(limit - len(q)).all()
        q += extra
    return [{"id": l.id, "prompt": l.prompt, "feature_name": l.feature_name,
             "user_feedback": l.user_feedback, "error_status": l.error_status} for l in q]


@router.post("/generate", response_model=list[EvalCaseOut])
def generate_labels(req: LabelRequest, db: Session = Depends(get_db)):
    created = []
    for log_id in req.log_ids:
        log = db.query(Log).filter(Log.id == log_id).first()
        if not log:
            continue

        dup, _reason = is_duplicate(db, log.prompt)
        if dup:
            continue

        label = label_log(log)

        rubric = label.get("rubric")
        eval_case = EvalCase(
            source_log_id=log.id,
            source_cluster_id=log.cluster_id,
            input=log.prompt,
            label_type=label["label_type"],
            expected_behavior=label.get("expected_behavior"),
            key_assertions=label.get("key_assertions", []),
            forbidden_assertions=label.get("forbidden_assertions", []),
            rubric=rubric,
            tags=label.get("tags", []),
            difficulty=label.get("difficulty", "medium"),
            confidence=label.get("confidence", 0.5),
            auto_labeled=True,
            status=DatasetStatus.draft,
            dedup_hash=text_hash(log.prompt),
        )
        db.add(eval_case)
        created.append(eval_case)

    db.commit()
    for c in created:
        db.refresh(c)
    return created
