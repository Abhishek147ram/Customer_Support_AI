from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class TicketCreate(BaseModel):
    customer_name: str = Field(..., min_length=2, max_length=128)
    customer_email: EmailStr
    subject: str = Field(..., min_length=5, max_length=256)
    description: str = Field(..., min_length=10, max_length=2000)


class TicketStatus(BaseModel):
    priority: str
    priority_score: float
    predicted_category: Optional[str]
    confidence: float
    escalated: bool
    escalated_reason: Optional[str]


class TicketResponse(BaseModel):
    id: int
    customer_name: str
    customer_email: EmailStr
    subject: str
    description: str
    ai_response: Optional[str]
    status: TicketStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TicketListResponse(BaseModel):
    tickets: List[TicketResponse]
    total: int
