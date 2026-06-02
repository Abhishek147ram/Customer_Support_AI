from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.logger import logger
from app.config.settings import settings
from app.models.ticket import Ticket
from app.schemas.ticket import TicketCreate
from app.services import OllamaClient, classify_ticket, detect_priority, should_escalate_ticket


async def get_ticket_by_id(session: AsyncSession, ticket_id: int) -> Optional[Ticket]:
    statement = select(Ticket).where(Ticket.id == ticket_id)
    result = await session.execute(statement)
    ticket = result.scalar_one_or_none()
    logger.debug(f"Queried ticket by id={ticket_id} result={ticket}")
    return ticket


async def list_tickets(session: AsyncSession, skip: int = 0, limit: int = 50) -> List[Ticket]:
    statement = select(Ticket).order_by(Ticket.created_at.desc()).offset(skip).limit(limit)
    result = await session.execute(statement)
    tickets = result.scalars().all()
    logger.debug(f"Retrieved {len(tickets)} tickets with skip={skip} limit={limit}")
    return tickets


def build_ticket_response(ticket: Ticket) -> Dict[str, Any]:
    return {
        "id": ticket.id,
        "customer_name": ticket.customer_name,
        "customer_email": ticket.customer_email,
        "subject": ticket.subject,
        "description": ticket.description,
        "ai_response": ticket.ai_response,
        "status": {
            "priority": ticket.priority,
            "priority_score": ticket.priority_score,
            "predicted_category": ticket.predicted_category,
            "confidence": ticket.confidence,
            "escalated": ticket.escalated,
            "escalated_reason": ticket.escalated_reason,
        },
        "created_at": ticket.created_at,
        "updated_at": ticket.updated_at,
    }


async def create_ticket(
    session: AsyncSession,
    ticket_in: TicketCreate,
    llm_client: OllamaClient,
) -> Tuple[Ticket, Dict[str, Any]]:
    category, confidence = classify_ticket(ticket_in.subject, ticket_in.description)
    priority, priority_score = detect_priority(ticket_in.subject, ticket_in.description)

    try:
        # Lightweight health check: if the model is not present, skip generation immediately.
        model_ok, health_info = await llm_client.check_health(warmup=False)
        if not model_ok:
            logger.warning(f"Skipping LLM generation; model not present: {health_info}")
            raise RuntimeError("LLM model not present")

        # Otherwise attempt generation; the generation method handles retries and finish_reason load.
        reply_data = await llm_client.generate_reply(
            customer_name=ticket_in.customer_name,
            subject=ticket_in.subject,
            description=ticket_in.description,
            category=category,
            priority=priority,
            priority_score=priority_score,
            escalation_threshold=settings.ticket_priority_threshold,
        )
    except Exception as exc:
        logger.error(f"LLM generation failed: {exc}")
        reply_data = None

    escalated = False
    escalated_reason = ""
    if reply_data is not None:
        escalated, escalated_reason = should_escalate_ticket(
            llm_confidence=reply_data.confidence_score,
            priority=priority,
            priority_score=priority_score,
            predicted_category=category,
        )
        ai_response = reply_data.recommended_reply
        confidence_score = reply_data.confidence_score
    else:
        escalated = True
        escalated_reason = "LLM service unavailable; human escalation required."
        ai_response = settings.fallback_response
        confidence_score = 0.0

    ticket = Ticket(
        customer_name=ticket_in.customer_name,
        customer_email=ticket_in.customer_email,
        subject=ticket_in.subject,
        description=ticket_in.description,
        priority=priority,
        priority_score=priority_score,
        predicted_category=category,
        confidence=confidence_score,
        ai_response=ai_response,
        escalated=escalated,
        escalated_reason=escalated_reason,
    )

    session.add(ticket)
    await session.commit()
    await session.refresh(ticket)

    escalation_payload: Dict[str, Any] = {}
    if escalated:
        escalation_payload = {
            "ticket_id": ticket.id,
            "customer_email": ticket.customer_email,
            "subject": ticket.subject,
            "priority": ticket.priority,
            "predicted_category": ticket.predicted_category,
            "escalation_reason": escalated_reason,
            "action_required": "Review ticket and provide human response.",
        }

    return ticket, escalation_payload


async def get_ticket_response(session: AsyncSession, ticket_id: int) -> Optional[Dict[str, Any]]:
    ticket = await get_ticket_by_id(session, ticket_id)
    if ticket is None:
        return None
    return build_ticket_response(ticket)
