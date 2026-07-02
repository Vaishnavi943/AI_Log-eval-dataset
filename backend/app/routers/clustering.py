from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import Log, Cluster, EvalCase
from app.schemas import ClusterRequest, ClusterOut
from app.services.clustering import cluster_logs

router = APIRouter(prefix="/clusters", tags=["clustering"])


@router.post("/run")
def run_clustering(req: ClusterRequest, db: Session = Depends(get_db)):
    clusters = cluster_logs(
        db,
        min_cluster_size=req.min_cluster_size,
        algorithm=req.algorithm,
        n_clusters=req.n_clusters,
    )
    return {"clusters_created": len(clusters)}


@router.get("", response_model=list[ClusterOut])
def list_clusters(db: Session = Depends(get_db)):
    clusters = db.query(Cluster).all()
    out = []
    for c in clusters:
        log_count = db.query(func.count(Log.id)).filter(Log.cluster_id == c.id).scalar()
        eval_count = db.query(func.count(EvalCase.id)).filter(
            EvalCase.source_cluster_id == c.id
        ).scalar()
        coverage = (eval_count / log_count) if log_count else 0.0
        c.eval_coverage = coverage
        out.append(ClusterOut(
            id=c.id, label=c.label, algorithm=c.algorithm,
            representative_log_ids=c.representative_log_ids,
            eval_coverage=coverage, log_count=log_count,
        ))
    db.commit()
    return out
