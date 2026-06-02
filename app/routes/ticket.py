from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.logger import logger
from app.config.settings import settings
from app.database.session import get_session
from app.schemas.ticket import TicketCreate, TicketResponse
from app.services.llm_service import OllamaClient
from app.services.ticket_service import create_ticket, get_ticket_response


class TicketProcessorMissing(Exception):
    pass

router = APIRouter()


@router.post(
    "/process",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Process a new support ticket",
)
async def process_ticket(
    ticket_in: TicketCreate,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> TicketResponse:
    """Process the incoming ticket, run classification, LLM reply generation, and store it."""
    logger.info(f"Processing new ticket for customer={ticket_in.customer_email}")

    # Readiness gate: if the LLM is not ready, only reject when human fallback is disabled.
    llm_ready = getattr(request.app.state, "llm_ready", False)
    if not llm_ready and not settings.fallback_to_human:
        logger.warning("LLM not ready; rejecting ticket processing to avoid false escalation")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM service not ready; please retry later",
        )
    if not llm_ready and settings.fallback_to_human:
        logger.warning("LLM not ready; processing ticket with fallback response")

    llm_client = OllamaClient()
    ticket, escalation_payload = await create_ticket(session, ticket_in, llm_client)
    if escalation_payload:
        logger.warning(f"Ticket requires escalation: {escalation_payload}")
    ticket_payload = await get_ticket_response(session, ticket.id)
    if ticket_payload is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to construct ticket response")
    return ticket_payload


@router.post(
    "/process-async",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Accept a ticket for asynchronous processing",
)
async def process_ticket_async(
    request: Request,
    ticket_in: TicketCreate,
) -> dict:
    """Enqueue the ticket for background processing without waiting for LLM generation."""
    logger.info(f"Enqueuing ticket for async processing customer={ticket_in.customer_email}")
    ticket_processor = getattr(request.app.state, "ticket_processor", None)
    if ticket_processor is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Asynchronous ticket processor is unavailable",
        )

    tracking_id = await ticket_processor.enqueue(ticket_in)
    return {"status": "accepted", "tracking_id": tracking_id}


@router.get(
    "/{ticket_id}",
    response_model=TicketResponse,
    summary="Get a ticket by ID",
)
async def get_ticket(ticket_id: int, session: AsyncSession = Depends(get_session)) -> TicketResponse:
    ticket_payload = await get_ticket_response(session, ticket_id)
    if ticket_payload is None:
        logger.warning(f"Ticket not found: {ticket_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    return ticket_payload
