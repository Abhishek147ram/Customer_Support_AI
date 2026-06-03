import time
import asyncio
from typing import Callable

from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.config.logger import logger
from app.config.settings import settings
from app.database.base import Base
from app.database.session import engine
from app.routes.health import router as health_router
from app.routes.ticket import router as ticket_router
from app.routes.tickets import router as tickets_router
from app.services.monitoring import MetricsCollector
from app.services.ticket_processor import TicketProcessor
from app.services.llm_service import OllamaClient
from app.utils.observability import build_error_response, get_request_context


app = FastAPI(
    title="AI-Powered Customer Support Automation System",
    version="0.1.0",
    description="Backend API for a local AI support ticket automation system.",
)

app.include_router(health_router)
app.include_router(ticket_router, prefix="/ticket", tags=["ticket"])
app.include_router(tickets_router, prefix="/tickets", tags=["tickets"])


@app.middleware("http")
async def measure_request_latency(request: Request, call_next: Callable):
    start_time = time.perf_counter()

    try:
        response = await call_next(request)

    except HTTPException as exc:
        logger.warning(
            f"HTTP error {request.method} {request.url.path}: {exc.detail}"
        )
        response = build_error_response(exc, exc.status_code)

    except Exception as exc:
        logger.exception(
            f"Unhandled exception {request.method} {request.url.path}"
        )
        response = build_error_response(
            exc,
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    elapsed = time.perf_counter() - start_time

    request.state.status_code = response.status_code
    response.headers["X-Process-Time"] = f"{elapsed:.3f}"

    context = get_request_context(request)

    metrics = getattr(request.app.state, "metrics", None)
    if metrics and settings.monitoring_enabled:
        metrics.increment("requests_total")
        metrics.record_latency("request_duration_seconds", elapsed)

    logger.info(
        f"Handled {context['method']} {context['path']} "
        f"status={response.status_code} "
        f"duration={elapsed:.3f} "
        f"query={context['query']} "
        f"client={context['client']}"
    )

    return response


@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request,
    exc: HTTPException,
):
    logger.warning(
        f"HTTPException {exc.status_code} on "
        f"{request.method} {request.url.path}: {exc.detail}"
    )

    return JSONResponse(
        content={"detail": exc.detail},
        status_code=exc.status_code,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    logger.error(
        f"Validation Error on {request.method} "
        f"{request.url.path}: {exc.errors()}"
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.errors(),
            "body": getattr(exc, "body", None),
        },
    )


@app.exception_handler(Exception)
async def unexpected_exception_handler(
    request: Request,
    exc: Exception,
):
    logger.exception(
        f"Unexpected error on "
        f"{request.method} {request.url.path}"
    )

    return JSONResponse(
        content={
            "detail": "Internal server error",
            "error": str(exc),
        },
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )

@app.on_event("startup")
async def startup_event() -> None:
    logger.info(
        f"Starting application with database_url={settings.database_url}"
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    app.state.metrics = MetricsCollector()

    app.state.llm_ready = False
    app.state.llm_health = {}
    app.state.ticket_processor = None
    app.state.llm_warmup_task = None

    async def _perform_llm_warmup() -> None:
        llm_client = OllamaClient()

        await asyncio.sleep(1)

        model_available, health_info = await llm_client.check_health(warmup=True)
        app.state.llm_ready = model_available
        app.state.llm_health = health_info

        if model_available:
            logger.info(f"Ollama model {settings.ollama_model} is available and warmed up")
            app.state.ticket_processor = TicketProcessor()
            await app.state.ticket_processor.start()
        else:
            logger.warning(
                f"Ollama is running but model '{settings.ollama_model}' is not ready: {health_info}"
            )
            app.state.ticket_processor = None
            if not settings.fallback_to_human:
                raise RuntimeError(f"Ollama warmup failed: {health_info}")

    if settings.ollama_health_check_enabled:
        if settings.fallback_to_human:
            app.state.llm_warmup_task = asyncio.create_task(_perform_llm_warmup())

            def _log_warmup_result(task: asyncio.Task) -> None:
                try:
                    task.result()
                except Exception as exc:
                    logger.error(f"Background Ollama warmup task failed: {exc}")

            app.state.llm_warmup_task.add_done_callback(_log_warmup_result)
        else:
            try:
                await _perform_llm_warmup()
            except Exception as exc:
                app.state.llm_ready = False
                app.state.llm_health = {"error": str(exc)}
                app.state.ticket_processor = None
                logger.warning(f"Ollama health/warmup check failed: {exc}")
                raise
    else:
        app.state.llm_health = {"message": "LLM health checks are disabled"}
        app.state.ticket_processor = TicketProcessor()
        await app.state.ticket_processor.start()


@app.on_event("shutdown")
async def shutdown_event() -> None:
    logger.info("Shutting down application")

    warmup_task = getattr(app.state, "llm_warmup_task", None)
    if warmup_task and not warmup_task.done():
        warmup_task.cancel()
        try:
            await warmup_task
        except asyncio.CancelledError:
            logger.info("Background Ollama warmup task was cancelled")

    ticket_processor = getattr(app.state, "ticket_processor", None)
    if ticket_processor:
        await ticket_processor.stop()


@app.get("/", summary="Root endpoint")
async def root() -> dict:
    return {
        "service": "AI-Powered Customer Support Automation System",
        "status": "ready",
    }

@app.get("/metrics", summary="Metrics endpoint")
async def metrics() -> Response:
    metrics_collector = getattr(app.state, "metrics", None)

    if not metrics_collector or not settings.monitoring_enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Metrics are unavailable",
        )

    return Response(
        content=metrics_collector.exposition_text(),
        media_type="text/plain",
    )
