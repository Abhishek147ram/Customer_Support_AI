from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text, func

from app.database.base import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String(128), nullable=False)
    customer_email = Column(String(256), nullable=False)
    subject = Column(String(256), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(String(32), nullable=False, default="normal")
    priority_score = Column(Float, nullable=False, default=0.0)
    predicted_category = Column(String(128), nullable=True)
    confidence = Column(Float, nullable=False, default=0.0)
    ai_response = Column(Text, nullable=True)
    escalated = Column(Boolean, default=False, nullable=False)
    escalated_reason = Column(String(256), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
