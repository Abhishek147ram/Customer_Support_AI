from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.logger import logger
from app.database.session import get_session
from app.schemas.ticket import TicketListResponse
from app.services.ticket_service import build_ticket_response, list_tickets

router = APIRouter()


@router.get("/", response_model=TicketListResponse, summary="List tickets")
async def read_tickets(
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
) -> TicketListResponse:
    """Return a paginated list of stored support tickets."""
    tickets = await list_tickets(session, skip=skip, limit=limit)
    logger.info(f"Listing tickets skip={skip} limit={limit} count={len(tickets)}")
    return {"tickets": [build_ticket_response(ticket) for ticket in tickets], "total": len(tickets)}
