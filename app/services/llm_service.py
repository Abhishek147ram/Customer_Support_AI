import json
import time
from typing import Any, Dict, List, Optional, Tuple

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.config.logger import logger
from app.config.settings import settings
from app.schemas.llm import LLMReply
from app.utils.prompt import build_ticket_reply_prompt


class OllamaClient:
    def __init__(self) -> None:

        self._client = httpx.AsyncClient(
            base_url=str(settings.ollama_url).rstrip("/"),
            headers={"Content-Type": "application/json"},
            timeout=httpx.Timeout(
                connect=settings.ollama_timeout_connect,
                read=settings.ollama_timeout_read,
                write=settings.ollama_timeout_write,
                pool=10.0,
            ),
            limits=httpx.Limits(
                max_keepalive_connections=5,
                max_connections=10,
            ),
        )

    async def check_health(
        self,
        warmup: bool = False
    ) -> Tuple[bool, Dict[str, Any]]:

        try:
            response = await self._client.get("/api/tags")

            response.raise_for_status()

            payload = response.json()

            models = self._extract_model_ids(payload)

            if settings.ollama_model not in models:

                return False, {
                    "configured_model": settings.ollama_model,
                    "available_models": models,
                }

            if warmup:

                start = time.perf_counter()

                try:

                    await self._wait_for_model_ready()

                    elapsed = round(
                        time.perf_counter() - start,
                        2
                    )

                    return True, {
                        "models": models,
                        "model_ready": True,
                        "warmup_time": elapsed,
                    }

                except Exception as exc:

                    elapsed = round(
                        time.perf_counter() - start,
                        2
                    )

                    logger.warning(
                        f"Warmup failed: {exc}"
                    )

                    return False, {
                        "error": str(exc),
                        "model_ready": False,
                        "warmup_time": elapsed,
                    }

            return True, {
                "models": models,
                "model_ready": False,
            }

        except Exception as exc:

            logger.exception(
                "LLM health check failed"
            )

            return False, {
                "error": str(exc)
            }

    async def generate_reply(
        self,
        customer_name: str,
        subject: str,
        description: str,
        category: str,
        priority: str,
        priority_score: float,
        escalation_threshold: Optional[float] = None,
    ) -> LLMReply:

        prompt = build_ticket_reply_prompt(
            customer_name=customer_name,
            subject=subject,
            description=description,
            category=category,
            priority=priority,
            priority_score=priority_score,
            escalation_threshold=escalation_threshold,
        )

        response_text = await self._generate_llm_response(
            prompt
        )

        json_text = self._extract_json_snippet(
            response_text
        )

        if json_text:

            try:
                return self._parse_structured_response(
                    json_text
                )

            except Exception as exc:

                logger.warning(
                    f"Structured parse failed: {exc}"
                )

        return LLMReply(
            recommended_reply=response_text.strip(),
            confidence_score=0.0,
            escalation_recommendation="yes",
            escalation_reason=(
                "Model returned unstructured output."
            ),
            follow_up_actions=(
                "Review response manually."
            ),
            raw_text=response_text,
        )

    @retry(
        retry=retry_if_exception_type(
            (httpx.RequestError, RuntimeError)
        ),
        stop=stop_after_attempt(
            settings.ollama_max_retries
        ),
        wait=wait_exponential(
            multiplier=settings.ollama_retry_backoff,
            max=settings.ollama_retry_max_delay,
        ),
        reraise=True,
    )
    async def _generate_llm_response(
        self,
        prompt: str
    ) -> str:

        payload = {
            "model": settings.ollama_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature":
                    settings.ollama_temperature,
                "num_predict":
                    settings.ollama_max_tokens,
            }
        }

        response = await self._client.post(
            "/api/generate",
            json=payload
        )

        response.raise_for_status()

        result = response.json()

        text = result.get("response")

        if text and str(text).strip():

            return str(text)

        raise RuntimeError(
            f"No valid output: {result}"
        )

    def _extract_model_ids(
        self,
        payload: Dict[str, Any]
    ) -> List[str]:

        models = []

        for model in payload.get(
            "models",
            []
        ):

            if not isinstance(
                model,
                dict
            ):
                continue

            if model.get("name"):
                models.append(
                    model["name"]
                )

            if model.get("model"):
                models.append(
                    model["model"]
                )

        return sorted(
            list(
                set(models)
            )
        )

    async def _wait_for_model_ready(
        self
    ) -> bool:

        payload = {
            "model":
                settings.ollama_model,
            "prompt":
                settings.ollama_model_warmup_prompt,
            "stream": False,
            "options": {
                "temperature": 0,
                "num_predict": 1,
            }
        }

        response = await self._client.post(
            "/api/generate",
            json=payload
        )

        response.raise_for_status()

        result = response.json()

        return bool(
            result.get("response")
        )

    def _extract_json_snippet(
        self,
        text: str
    ) -> Optional[str]:

        start = text.find("{")

        if start == -1:
            return None

        depth = 0

        for idx, ch in enumerate(
            text[start:],
            start=start
        ):

            if ch == "{":
                depth += 1

            elif ch == "}":

                depth -= 1

                if depth == 0:

                    return text[
                        start:idx + 1
                    ]

        return None

    def _parse_structured_response(
        self,
        text: str
    ) -> LLMReply:

        payload = json.loads(text)

        payload.setdefault(
            "raw_text",
            text
        )

        for field in [
            "follow_up_actions",
            "recommended_reply",
            "escalation_reason",
        ]:

            value = payload.get(field)

            if isinstance(
                value,
                list
            ):

                payload[field] = "\n".join(
                    str(item)
                    for item in value
                )

        payload.setdefault(
            "confidence_score",
            0.0
        )

        payload.setdefault(
            "escalation_recommendation",
            "yes"
        )

        payload.setdefault(
            "follow_up_actions",
            "Manual review required"
        )

        return LLMReply(
            **payload
        )
