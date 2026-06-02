from typing import Optional

from pydantic import BaseModel


class LLMReply(BaseModel):
    recommended_reply: str
    confidence_score: float
    escalation_recommendation: str
    escalation_reason: Optional[str]
    follow_up_actions: str
    raw_text: str


class LLMResponse(BaseModel):
    reply: LLMReply
