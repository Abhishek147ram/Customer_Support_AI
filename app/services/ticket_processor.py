import asyncio
from typing import Any, Dict, Optional

from app.config.logger import logger
from app.database.session import AsyncSessionLocal
from app.schemas.ticket import TicketCreate
from app.services.llm_service import OllamaClient
from app.services.queue import TicketQueue
from app.services.ticket_service import create_ticket


class TicketProcessor:
    def __init__(self) -> None:
        self._queue = TicketQueue(self._handle_task)
        self._started = False

    async def start(self) -> None:
        if not self._started:
            await self._queue.start()
            self._started = True
            logger.info("TicketProcessor started")

    async def stop(self) -> None:
        if self._started:
            await self._queue.stop()
            self._started = False
            logger.info("TicketProcessor stopped")

    async def enqueue(self, ticket_in: TicketCreate) -> str:
        payload = {"ticket_data": ticket_in}
        return await self._queue.enqueue_ticket(payload)

    async def _handle_task(self, payload: Dict[str, Any]) -> None:
        ticket_in: Optional[TicketCreate] = payload.get("ticket_data")
        if ticket_in is None:
            logger.error("Queued task missing ticket_data")
            return

        async with AsyncSessionLocal() as session:
            llm_client = OllamaClient()
            try:
                await create_ticket(session, ticket_in, llm_client)
                logger.info("Queued ticket processed successfully")
            except Exception as exc:
                logger.exception(f"Queued ticket processing failed: {exc}")
