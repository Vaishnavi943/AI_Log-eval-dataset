import random
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models import Log


def sample_logs(db: Session, mode: str, n: int):
    if mode == "failure_biased":
        # over-select logs with negative feedback, retries, or errors
        failing = (
            db.query(Log)
            .filter(
                or_(
                    Log.user_feedback == "negative",
                    Log.retry_count > 0,
                    Log.error_status.isnot(None),
                )
            )
            .all()
        )
        healthy = db.query(Log).filter(
            Log.user_feedback != "negative",
            Log.retry_count == 0,
            Log.error_status.is_(None),
        ).limit(n).all()

        pool = failing + healthy
        random.shuffle(failing)
        target_failing = min(len(failing), int(n * 0.7))
        target_healthy = n - target_failing
        result = failing[:target_failing] + healthy[:target_healthy]
        random.shuffle(result)
        return result[:n]

    elif mode == "diversity":
        # naive diversity sampling: one per feature_name/cluster combo, round robin
        logs = db.query(Log).all()
        buckets = {}
        for log in logs:
            key = (log.feature_name, log.cluster_id)
            buckets.setdefault(key, []).append(log)
        for v in buckets.values():
            random.shuffle(v)

        result = []
        keys = list(buckets.keys())
        i = 0
        while len(result) < n and any(buckets.values()):
            key = keys[i % len(keys)]
            if buckets[key]:
                result.append(buckets[key].pop())
            i += 1
            if i > n * 10:
                break
        return result[:n]

    # default: random sampling
    total = db.query(Log).count()
    if total == 0:
        return []
    offset = random.randint(0, max(0, total - n))
    return db.query(Log).offset(offset).limit(n).all()
