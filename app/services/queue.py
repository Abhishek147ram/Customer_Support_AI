import asyncio
import uuid
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Optional

from app.config.logger import logger
from app.config.settings import settings

TaskPayload = Dict[str, Any]
TaskHandler = Callable[[TaskPayload], asyncio.Future]


class QueueAdapter(ABC):
    @abstractmethod
    async def enqueue(self, payload: TaskPayload) -> str:
        raise NotImplementedError

    @abstractmethod
    def size(self) -> int:
        raise NotImplementedError


class InMemoryQueueAdapter(QueueAdapter):
    def __init__(self, handler: TaskHandler) -> None:
        self._queue: asyncio.Queue[TaskPayload] = asyncio.Queue()
        self._handler = handler
        self._worker_task: Optional[asyncio.Task[None]] = None
        self._running = False

    async def start(self) -> None:
        if not self._running:
            self._running = True
            self._worker_task = asyncio.create_task(self._worker())
            logger.info("Started in-memory task queue worker")

    async def stop(self) -> None:
        self._running = False
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                logger.info("In-memory queue worker cancelled")

    async def enqueue(self, payload: TaskPayload) -> str:
        task_id = str(uuid.uuid4())
        payload["task_id"] = task_id
        await self._queue.put(payload)
        logger.info(f"Enqueued task {task_id} queue_size={self._queue.qsize()}")
        return task_id

    def size(self) -> int:
        return self._queue.qsize()

    async def _worker(self) -> None:
        while self._running:
            payload = await self._queue.get()
            task_id = payload.get("task_id")
            logger.info(f"Processing queued task {task_id}")
            try:
                await self._handler(payload)
            except Exception as exc:
                logger.exception(f"Queued task {task_id} failed: {exc}")
            finally:
                self._queue.task_done()


class TicketQueue:
    def __init__(self, handler: TaskHandler) -> None:
        self._adapter = InMemoryQueueAdapter(handler)

    async def start(self) -> None:
        if settings.queue_mode == "local":
            await self._adapter.start()

    async def stop(self) -> None:
        await self._adapter.stop()

    async def enqueue_ticket(self, payload: TaskPayload) -> str:
        return await self._adapter.enqueue(payload)

    def size(self) -> int:
        return self._adapter.size()
