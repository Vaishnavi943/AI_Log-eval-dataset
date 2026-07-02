from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class LogOut(BaseModel):
    id: str
    prompt: str
    system_prompt: Optional[str] = None
    response: str
    model: str
    feature_name: str
    latency_ms: Optional[int] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    user_feedback: Optional[str] = None
    retry_count: int
    error_status: Optional[str] = None
    is_redacted: bool
    redaction_method: Optional[str] = None
    cluster_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ClusterOut(BaseModel):
    id: str
    label: Optional[str]
    algorithm: str
    representative_log_ids: List[str]
    eval_coverage: float
    log_count: int = 0

    class Config:
        from_attributes = True


class EvalCaseOut(BaseModel):
    id: str
    source_log_id: Optional[str]
    source_cluster_id: Optional[str]
    input: str
    label_type: str
    expected_behavior: Optional[str]
    key_assertions: List[str]
    forbidden_assertions: List[str]
    rubric: Optional[Dict[str, Any]]
    tags: List[str]
    difficulty: str
    confidence: float
    auto_labeled: bool
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class ReviewAction(BaseModel):
    action: str  # approve | edit | reject
    reviewer: str = "anonymous"
    reason: Optional[str] = None
    edits: Optional[Dict[str, Any]] = None  # fields to overwrite on approve/edit


class SeedRequest(BaseModel):
    count: int = 1000


class LogCreate(BaseModel):
    prompt: str
    response: str
    system_prompt: Optional[str] = None
    model: str = "manual-entry"
    feature_name: str = "manual"
    user_feedback: Optional[str] = None
    error_status: Optional[str] = None
    retry_count: int = 0


class SampleRequest(BaseModel):
    mode: str = "random"  # random | failure_biased | diversity
    n: int = 50


class ClusterRequest(BaseModel):
    min_cluster_size: int = 5
    algorithm: str = "hdbscan"  # hdbscan | kmeans
    n_clusters: Optional[int] = None  # for kmeans


class LabelRequest(BaseModel):
    log_ids: List[str]


class DatasetHealth(BaseModel):
    total_cases: int
    by_status: Dict[str, int]
    by_difficulty: Dict[str, int]
    by_label_type: Dict[str, int]
    auto_labeled_pct: float
    human_reviewed_pct: float
