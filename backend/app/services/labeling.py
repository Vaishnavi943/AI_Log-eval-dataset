import json
from groq import Groq

from app.config import settings
from app.models import Log, LabelType

_client = None

SYSTEM_PROMPT = """You are building an evaluation dataset from production LLM logs.
Given a logged interaction, decide the best eval type and produce a label.

Respond ONLY with JSON, no markdown fences, matching this schema:
{
  "label_type": "golden_answer" | "rubric" | "expected_refusal",
  "expected_behavior": "string describing what a correct response should do, or a golden answer",
  "key_assertions": ["short assertion", ...],
  "forbidden_assertions": ["short assertion", ...],
  "rubric": {"criterion": weight_float, ...} or null,
  "tags": ["short-tag", ...],
  "difficulty": "easy" | "medium" | "hard",
  "confidence": float between 0 and 1
}

Guidance:
- Use "expected_refusal" for unsafe/policy-violating requests.
- Use "golden_answer" when there's a clear correct answer (factual, deterministic tasks).
- Use "rubric" for open-ended or subjective responses (writing, summaries, advice).
- confidence should reflect how sure you are the label is correct and complete;
  low confidence (<0.7) sends this case to human review.
"""


def get_client():
    global _client
    if _client is None:
        _client = Groq(api_key=settings.groq_api_key)
    return _client


def label_log(log: Log) -> dict:
    """Calls a Groq-hosted model as a judge to propose an eval label for a single log."""
    client = get_client()
    user_msg = (
        f"Feature: {log.feature_name}\n"
        f"System prompt: {log.system_prompt or 'n/a'}\n"
        f"User prompt: {log.prompt}\n"
        f"Model response: {log.response}\n"
        f"User feedback: {log.user_feedback or 'none'}\n"
        f"Error status: {log.error_status or 'none'}\n"
        f"Retry count: {log.retry_count}"
    )
    resp = client.chat.completions.create(
        model=settings.groq_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        response_format={"type": "json_object"},
        temperature=0.2,
        max_tokens=800,
    )
    text = resp.choices[0].message.content.strip()
    data = json.loads(text)

    # normalize enum value
    if data.get("label_type") not in {t.value for t in LabelType}:
        data["label_type"] = LabelType.rubric.value

    return data
