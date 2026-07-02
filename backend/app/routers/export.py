import json
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import EvalCase, DatasetStatus
from app.schemas import DatasetHealth

router = APIRouter(prefix="/export", tags=["export"])


@router.get("/jsonl")
def export_jsonl(db: Session = Depends(get_db)):
    cases = db.query(EvalCase).filter(EvalCase.status == DatasetStatus.approved).all()

    def gen():
        for c in cases:
            row = {
                "input": c.input,
                "expected_behavior": c.expected_behavior,
                "label_type": c.label_type,
                "key_assertions": c.key_assertions,
                "forbidden_assertions": c.forbidden_assertions,
                "rubric": c.rubric,
                "tags": c.tags,
                "difficulty": c.difficulty,
                "source_cluster": c.source_cluster_id,
                "date_added": c.created_at.isoformat(),
            }
            yield json.dumps(row) + "\n"

    return StreamingResponse(gen(), media_type="application/x-ndjson",
                              headers={"Content-Disposition": "attachment; filename=eval_dataset.jsonl"})


@router.get("/health", response_model=DatasetHealth)
def dataset_health(db: Session = Depends(get_db)):
    total = db.query(EvalCase).count()

    by_status = {}
    for status in DatasetStatus:
        by_status[status.value] = db.query(EvalCase).filter(EvalCase.status == status).count()

    by_difficulty = {}
    for row in db.query(EvalCase.difficulty, func.count(EvalCase.id)).group_by(EvalCase.difficulty).all():
        by_difficulty[row[0]] = row[1]

    by_label_type = {}
    for row in db.query(EvalCase.label_type, func.count(EvalCase.id)).group_by(EvalCase.label_type).all():
        by_label_type[row[0]] = row[1]

    auto = db.query(EvalCase).filter(EvalCase.auto_labeled.is_(True)).count()
    human = total - auto

    return DatasetHealth(
        total_cases=total,
        by_status=by_status,
        by_difficulty=by_difficulty,
        by_label_type=by_label_type,
        auto_labeled_pct=round((auto / total) * 100, 1) if total else 0.0,
        human_reviewed_pct=round((human / total) * 100, 1) if total else 0.0,
    )
