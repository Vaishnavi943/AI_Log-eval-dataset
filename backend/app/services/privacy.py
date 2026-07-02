import re

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}")
SECRET_RE = re.compile(r"(sk-[a-zA-Z0-9]{10,}|api[_-]?key\s*[:=]\s*['\"]?[a-zA-Z0-9]{10,})", re.I)
# very small illustrative name list matcher; swap for a NER model in production
NAME_HINT_RE = re.compile(r"\bmy name is ([A-Z][a-z]+(?: [A-Z][a-z]+)?)")


def redact(text: str):
    """Redacts emails, phone numbers, secrets, and simple self-identified names.
    Returns (redacted_text, redacted_fields, was_redacted).
    """
    redacted_fields = []
    out = text

    if EMAIL_RE.search(out):
        out = EMAIL_RE.sub("[REDACTED_EMAIL]", out)
        redacted_fields.append("email")

    if SECRET_RE.search(out):
        out = SECRET_RE.sub("[REDACTED_SECRET]", out)
        redacted_fields.append("secret")

    if PHONE_RE.search(out):
        out = PHONE_RE.sub("[REDACTED_PHONE]", out)
        redacted_fields.append("phone")

    if NAME_HINT_RE.search(out):
        out = NAME_HINT_RE.sub("my name is [REDACTED_NAME]", out)
        redacted_fields.append("name")

    return out, redacted_fields, len(redacted_fields) > 0


REDACTION_METHOD = "regex_pii_v1"
