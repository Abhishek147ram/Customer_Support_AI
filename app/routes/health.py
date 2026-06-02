from fastapi import APIRouter, Request
from app.config.logger import logger

router = APIRouter()


@router.get("/health", summary="Health check endpoint")
async def health_check() -> dict:
    """Return the current service health status."""
    logger.info("Health check request received")
    return {"status": "ok", "message": "AI support automation is running"}


@router.get("/health/llm", summary="LLM health check endpoint")
async def llm_health_check(request: Request) -> dict:
    """Return the current Ollama health and model availability."""
    logger.info("LLM health check request received")
    llm_ready = getattr(request.app.state, "llm_ready", False)
    llm_health = getattr(request.app.state, "llm_health", {})
    status = "ok" if llm_ready else "degraded"
    return {
        "status": status,
        "llm_ready": llm_ready,
        "llm_health": llm_health,
    }
