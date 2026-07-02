import hashlib
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.orm import Session

from app.models import EvalCase

SIMILARITY_THRESHOLD = 0.92


def text_hash(text: str) -> str:
    return hashlib.sha256(text.strip().lower().encode()).hexdigest()


def is_duplicate(db: Session, input_text: str, embedding: list[float] | None = None):
    """Exact-hash check first (cheap), then embedding-similarity check if a vector is given."""
    h = text_hash(input_text)
    exact = db.query(EvalCase).filter(EvalCase.dedup_hash == h).first()
    if exact:
        return True, "exact_hash_match"

    if embedding is not None:
        existing = db.query(EvalCase).all()
        # NOTE: for large datasets swap this for a vector index (pgvector, faiss);
        # fine for portfolio-scale datasets.
        candidates = [
            (e, e.rubric.get("_embedding")) for e in existing
            if e.rubric and "_embedding" in e.rubric
        ]
        if candidates:
            vecs = np.array([c[1] for c in candidates])
            sims = cosine_similarity([embedding], vecs)[0]
            best_idx = int(np.argmax(sims))
            if sims[best_idx] >= SIMILARITY_THRESHOLD:
                return True, f"embedding_similarity_{sims[best_idx]:.2f}"

    return False, None
