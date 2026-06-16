import json
import re
from dataclasses import dataclass

from openai import OpenAI

from app.core.config import get_settings
from app.schemas.email import EmailGenerateRequest


@dataclass
class AIEmailResult:
    subject: str
    body: str
    call_to_action: str | None
    score: int
    improvement_tips: list[str]


def _extract_json(text: str) -> dict:
    """Extract JSON from a model response even if markdown fences are returned."""
    cleaned = text.strip()
    cleaned = re.sub(r"^```json\s*", "", cleaned)
    cleaned = re.sub(r"^```\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise


def _validate_score(value) -> int:
    try:
        score = int(value)
    except (TypeError, ValueError):
        return 75
    return max(0, min(100, score))


def _fallback_email(payload: EmailGenerateRequest) -> AIEmailResult:
    subject = f"Regarding {payload.purpose[:70]}"
    body = (
        f"Dear {payload.recipient_type},\n\n"
        f"I hope you are doing well. I am writing regarding {payload.purpose}.\n\n"
        f"Key details:\n{payload.key_points}\n\n"
        "Please let me know if you need any further information.\n\n"
        "Best regards"
    )
    return AIEmailResult(
        subject=subject,
        body=body,
        call_to_action="Please let me know your thoughts.",
        score=70,
        improvement_tips=["Add a valid OPENAI_API_KEY in .env for stronger AI output."],
    )


def generate_email_with_ai(payload: EmailGenerateRequest) -> AIEmailResult:
    settings = get_settings()

    if settings.ai_provider.lower() != "openai" or not settings.openai_api_key:
        return _fallback_email(payload)

    client = OpenAI(api_key=settings.openai_api_key)

    system_prompt = """
You are an expert business communication assistant.
Generate polished, ready-to-send emails.
Return ONLY valid JSON with these keys:
subject: string
body: string
call_to_action: string or null
score: integer from 0 to 100
improvement_tips: array of strings
Rules:
- Do not invent fake facts.
- Keep the email aligned with the requested tone, language, and length.
- Make it human, clear, and professional.
- Do not include markdown.
""".strip()

    user_prompt = f"""
Purpose: {payload.purpose}
Recipient type: {payload.recipient_type}
Tone: {payload.tone}
Language: {payload.language}
Length: {payload.length}
Include subject: {payload.include_subject}
Include call to action: {payload.include_call_to_action}
Key points:
{payload.key_points}
""".strip()

    try:
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.6,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content or "{}"
        data = _extract_json(content)
        return AIEmailResult(
            subject=str(data.get("subject") or f"Regarding {payload.purpose[:70]}").strip(),
            body=str(data.get("body") or "").strip(),
            call_to_action=(str(data.get("call_to_action")).strip() if data.get("call_to_action") else None),
            score=_validate_score(data.get("score")),
            improvement_tips=[str(item) for item in data.get("improvement_tips", [])][:5],
        )
    except Exception as exc:
        fallback = _fallback_email(payload)
        fallback.improvement_tips.insert(0, f"AI provider error: {type(exc).__name__}")
        return fallback
