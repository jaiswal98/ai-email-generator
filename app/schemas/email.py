from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

Tone = Literal["Professional", "Friendly", "Formal", "Persuasive", "Apologetic", "Confident"]
Length = Literal["Short", "Medium", "Detailed"]


class EmailGenerateRequest(BaseModel):
    purpose: str = Field(..., min_length=5, max_length=500)
    recipient_type: str = Field(..., min_length=2, max_length=100)
    tone: Tone = "Professional"
    key_points: str = Field(..., min_length=5, max_length=1500)
    language: str = Field(default="English", min_length=2, max_length=80)
    length: Length = "Medium"
    include_subject: bool = True
    include_call_to_action: bool = True


class EmailGeneratedOut(BaseModel):
    id: int
    subject: str
    body: str
    call_to_action: str | None = None
    score: int
    improvement_tips: list[str] = []


class EmailHistoryOut(BaseModel):
    id: int
    purpose: str
    recipient_type: str
    tone: str
    subject: str
    body: str
    call_to_action: str | None
    score: int
    language: str
    created_at: datetime

    model_config = {"from_attributes": True}
