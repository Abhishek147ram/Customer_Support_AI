from time import perf_counter
from typing import Any, Dict

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from loguru import logger


def get_request_context(request: Request) -> Dict[str, Any]:
    return {
        "method": request.method,
        "path": request.url.path,
        "query": dict(request.query_params),
        "client": request.client.host if request.client else "unknown",
    }


def build_error_response(exc: Exception, status_code: int) -> JSONResponse:
    payload = {
        "detail": str(exc) if status_code < 500 else "Internal server error",
        "status_code": status_code,
    }
    return JSONResponse(content=payload, status_code=status_code)


def timing_middleware(request: Request, response_time: float) -> None:
    context = get_request_context(request)
    logger.info(
        "Handled request {method} {path} status={status_code} duration={duration}s query={query} client={client}",
        method=context["method"],
        path=context["path"],
        status_code=getattr(request.state, "status_code", "unknown"),
        duration=f"{response_time:.3f}",
        query=context["query"],
        client=context["client"],
    )
