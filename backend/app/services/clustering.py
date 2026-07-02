import numpy as np
from sqlalchemy.orm import Session
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import normalize

from app.models import Log, Cluster

# TF-IDF + SVD instead of sentence-transformers/torch: no heavyweight model download,
# no ~1-2GB torch wheel, and it fits comfortably inside Vercel's serverless bundle limit.
EMBEDDING_DIM = 64


def embed_logs(db: Session, logs: list[Log], all_texts_for_fit: list[str] | None = None):
    """Vectorizes prompts with TF-IDF, reduces to EMBEDDING_DIM dims with SVD, stores on each log.

    `all_texts_for_fit` lets the caller fit the vectorizer/SVD on the full corpus (recommended)
    even when only a subset of `logs` is being (re)embedded.
    """
    texts = [log.prompt for log in logs]
    fit_corpus = all_texts_for_fit if all_texts_for_fit else texts

    vectorizer = TfidfVectorizer(max_features=5000, stop_words="english", ngram_range=(1, 2))
    tfidf_fit = vectorizer.fit_transform(fit_corpus)

    n_components = min(EMBEDDING_DIM, tfidf_fit.shape[1] - 1, tfidf_fit.shape[0] - 1)
    n_components = max(n_components, 2)
    svd = TruncatedSVD(n_components=n_components, random_state=42)
    svd.fit(tfidf_fit)

    tfidf_subset = vectorizer.transform(texts)
    vectors = normalize(svd.transform(tfidf_subset))

    for log, vec in zip(logs, vectors):
        log.embedding = vec.tolist()
    db.bulk_save_objects(logs)
    db.commit()
    return vectors


def _try_hdbscan(vectors: np.ndarray, min_cluster_size: int):
    try:
        from sklearn.cluster import HDBSCAN  # available in scikit-learn >= 1.3
        model = HDBSCAN(min_cluster_size=min_cluster_size, metric="euclidean")
        labels = model.fit_predict(vectors)
        return labels
    except ImportError:
        return None


def cluster_logs(db: Session, min_cluster_size: int = 5, algorithm: str = "hdbscan",
                  n_clusters: int | None = None):
    """(Re)embeds all logs against the current corpus, clusters them, and (re)creates Cluster rows.

    TF-IDF vocabulary depends on the whole corpus, so logs are re-embedded together each run
    rather than incrementally (cheap at portfolio-scale log volumes).
    """
    logs = db.query(Log).all()
    if not logs:
        return []

    texts = [log.prompt for log in logs]
    embed_logs(db, logs, all_texts_for_fit=texts)

    vectors = np.array([log.embedding for log in logs])

    labels = None
    used_algo = algorithm
    if algorithm == "hdbscan":
        labels = _try_hdbscan(vectors, min_cluster_size)
        if labels is None:
            used_algo = "kmeans"  # fallback if HDBSCAN unavailable in this sklearn version

    if labels is None:
        k = n_clusters or max(2, len(logs) // max(min_cluster_size, 1))
        k = min(k, len(logs))
        km = KMeans(n_clusters=k, n_init="auto", random_state=42)
        labels = km.fit_predict(vectors)

    # clear old cluster assignments
    db.query(Log).update({Log.cluster_id: None})
    db.query(Cluster).delete()
    db.commit()

    grouped: dict[int, list[Log]] = {}
    for log, label in zip(logs, labels):
        grouped.setdefault(int(label), []).append(log)

    clusters = []
    for label, members in grouped.items():
        if label == -1:
            continue  # HDBSCAN noise points stay unclustered
        rep_ids = [m.id for m in members[:3]]
        rep_text = " | ".join(m.prompt[:40] for m in members[:3])
        cluster = Cluster(
            label=rep_text[:120],
            algorithm=used_algo,
            representative_log_ids=rep_ids,
        )
        db.add(cluster)
        db.flush()  # get cluster.id
        for m in members:
            m.cluster_id = cluster.id
        clusters.append(cluster)

    db.commit()
    return clusters
