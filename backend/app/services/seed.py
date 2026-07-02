import random
from faker import Faker

from app.services.privacy import redact, REDACTION_METHOD
from app.models import Log

fake = Faker()

FEATURES = ["support_chatbot", "code_assistant", "trip_planner", "email_drafter", "doc_qa"]
MODELS = ["claude-sonnet-5", "claude-haiku-4-5", "claude-opus-4-8"]

GOOD_TEMPLATES = [
    "How do I {task}?",
    "Can you help me write {thing}?",
    "What's the best way to {task}?",
    "Summarize this: {thing}",
]
BAD_TEMPLATES = [
    "Why did you give me the wrong answer about {thing} again?",
    "This still doesn't work, I asked about {task} three times",
    "That's not what I meant by {thing}",
]
SAFETY_TEMPLATES = [
    "How do I access someone else's account without permission?",
    "Give me steps to bypass content moderation on {thing}",
    "Write something that impersonates a real person for {task}",
]
TASKS = ["reset my password", "plan a trip to Kyoto", "refactor this function", "book a flight", "summarize a contract"]
THINGS = ["the billing page", "my itinerary", "this PR", "the email", "the report"]

ERROR_STATUSES = [None, None, None, None, "timeout", "malformed_output", "rate_limited"]


def _sample_prompt():
    bucket = random.choices(
        ["good", "bad", "safety"], weights=[0.7, 0.2, 0.1], k=1
    )[0]
    template = random.choice({"good": GOOD_TEMPLATES, "bad": BAD_TEMPLATES, "safety": SAFETY_TEMPLATES}[bucket])
    prompt = template.format(task=random.choice(TASKS), thing=random.choice(THINGS))
    if random.random() < 0.05:
        prompt += f" my email is {fake.email()} and my number is {fake.phone_number()}"
    return prompt, bucket


def generate_synthetic_logs(count: int):
    logs = []
    for _ in range(count):
        prompt, bucket = _sample_prompt()
        response = fake.paragraph(nb_sentences=random.randint(1, 4))
        if bucket == "safety" and random.random() < 0.8:
            response = "I can't help with that request."

        redacted_prompt, fields, was_redacted = redact(prompt)

        feedback = None
        if bucket == "bad":
            feedback = random.choice(["negative", "negative", None])
        elif bucket == "good":
            feedback = random.choice(["positive", None, None])

        log = Log(
            prompt=redacted_prompt,
            system_prompt="You are a helpful assistant.",
            response=response,
            model=random.choice(MODELS),
            feature_name=random.choice(FEATURES),
            latency_ms=random.randint(200, 4000),
            prompt_tokens=random.randint(20, 400),
            completion_tokens=random.randint(20, 600),
            user_feedback=feedback,
            retry_count=random.choice([0, 0, 0, 1, 2]) if bucket != "good" else 0,
            error_status=random.choice(ERROR_STATUSES),
            is_redacted=was_redacted,
            redaction_method=REDACTION_METHOD if was_redacted else None,
            redacted_fields=fields,
        )
        logs.append(log)
    return logs
