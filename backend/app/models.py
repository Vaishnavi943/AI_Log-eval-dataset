import uuid
import enum
from datetime import datetime

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, Enum, JSON
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship

from app.database import Base


def gen_uuid():
    return str(uuid.uuid4())


class DatasetStatus(str, enum.Enum):
    draft = "draft"
    approved = "approved"
    rejected = "rejected"
    deprecated = "deprecated"


class LabelType(str, enum.Enum):
    golden_answer = "golden_answer"
    rubric = "rubric"
    expected_refusal = "expected_refusal"


# ---------------------------------------------------------------------------
# Phase 1: unified log schema
# ---------------------------------------------------------------------------
class Log(Base):
    __tablename__ = "logs"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)

    prompt = Column(Text, nullable=False)
    system_prompt = Column(Text, nullable=True)
    response = Column(Text, nullable=False)

    model = Column(String, nullable=False)
    feature_name = Column(String, index=True, nullable=False)

    latency_ms = Column(Integer, nullable=True)
    prompt_tokens = Column(Integer, nullable=True)
    completion_tokens = Column(Integer, nullable=True)

    user_feedback = Column(String, nullable=True)  # 'positive' | 'negative' | None
    retry_count = Column(Integer, default=0)
    error_status = Column(String, nullable=True)  # e.g. 'timeout', 'malformed_output', None

    # privacy controls (Phase 1.2)
    is_redacted = Column(Boolean, default=False)
    redaction_method = Column(String, nullable=True)  # e.g. 'regex_pii_v1'
    redacted_fields = Column(ARRAY(String), default=list)

    # clustering
    cluster_id = Column(UUID(as_uuid=False), ForeignKey("clusters.id"), nullable=True)
    embedding = Column(ARRAY(Float), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    cluster = relationship("Cluster", back_populates="logs")


# ---------------------------------------------------------------------------
# Phase 2: clusters
# ---------------------------------------------------------------------------
class Cluster(Base):
    __tablename__ = "clusters"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    label = Column(String, nullable=True)  # human-readable, assigned from representative examples
    algorithm = Column(String, default="hdbscan")
    representative_log_ids = Column(ARRAY(String), default=list)
    eval_coverage = Column(Float, default=0.0)  # fraction of cluster already covered by eval cases
    created_at = Column(DateTime, default=datetime.utcnow)

    logs = relationship("Log", back_populates="cluster")


# ---------------------------------------------------------------------------
# Phase 3/4: eval cases + review
# ---------------------------------------------------------------------------
class EvalCase(Base):
    __tablename__ = "eval_cases"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    source_log_id = Column(UUID(as_uuid=False), ForeignKey("logs.id"), nullable=True)
    source_cluster_id = Column(UUID(as_uuid=False), ForeignKey("clusters.id"), nullable=True)

    input = Column(Text, nullable=False)
    label_type = Column(Enum(LabelType), nullable=False)

    expected_behavior = Column(Text, nullable=True)   # golden answer / expected refusal text
    key_assertions = Column(ARRAY(String), default=list)
    forbidden_assertions = Column(ARRAY(String), default=list)
    rubric = Column(JSON, nullable=True)               # {criterion: weight}

    tags = Column(ARRAY(String), default=list)
    difficulty = Column(String, default="medium")       # easy | medium | hard

    confidence = Column(Float, default=0.0)
    auto_labeled = Column(Boolean, default=True)

    status = Column(Enum(DatasetStatus), default=DatasetStatus.draft, index=True)
    dedup_hash = Column(String, index=True, nullable=True)
    rejected_reason = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    review_events = relationship("ReviewEvent", back_populates="eval_case")


class ReviewEvent(Base):
    __tablename__ = "review_events"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    eval_case_id = Column(UUID(as_uuid=False), ForeignKey("eval_cases.id"), nullable=False)

    action = Column(String, nullable=False)  # approve | edit | reject
    reviewer = Column(String, default="anonymous")
    diff = Column(JSON, nullable=True)        # what changed
    reason = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    eval_case = relationship("EvalCase", back_populates="review_events")


class EvalRun(Base):
    __tablename__ = "eval_runs"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    dataset_snapshot_size = Column(Integer, default=0)
    model_endpoint = Column(String, nullable=True)
    pass_rate = Column(Float, nullable=True)
    results = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
