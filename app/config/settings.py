from typing import List, Optional, Literal
from pydantic import Field, AnyUrl, ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    database_url: str = Field(
        ...,
        validation_alias="DATABASE_URL",
        description="Database connection URL"
    )

    ollama_url: AnyUrl = Field(
        ...,
        validation_alias="OLLAMA_URL",
        description="Ollama API base URL (e.g., http://localhost:11434)"
    )

    ollama_model: str = Field(
        "llama3.2:1b",  # Default to smaller, faster model for laptops
        validation_alias="OLLAMA_MODEL",
        description="Name of the Ollama model to use"
    )

    # Timeout settings for LLM generation requests (NOT health checks)
    ollama_timeout_connect: int = Field(
        10,
        validation_alias="OLLAMA_TIMEOUT_CONNECT",
        ge=1,
        description="Connection timeout for Ollama API in seconds"
    )

    ollama_timeout_read: int = Field(
        120, 
        validation_alias="OLLAMA_TIMEOUT_READ",
        ge=10,
        description="Read timeout for Ollama API in seconds (generation time)"
    )

    ollama_timeout_write: int = Field(
        30,
        validation_alias="OLLAMA_TIMEOUT_WRITE",
        ge=5,
        description="Write timeout for sending requests to Ollama in seconds"
    )

    ollama_max_retries: int = Field(
        6,
        validation_alias="OLLAMA_MAX_RETRIES",
        ge=0,
        le=10,
        description="Maximum retry attempts for failed LLM requests"
    )

    ollama_retry_backoff: float = Field(
        2.0,
        validation_alias="OLLAMA_RETRY_BACKOFF",
        ge=1.0,
        description="Exponential backoff multiplier for retries"
    )

    ollama_retry_max_delay: float = Field(
        30.0,
        validation_alias="OLLAMA_RETRY_MAX_DELAY",
        ge=5.0,
        description="Maximum delay between retries in seconds"
    )

    ollama_temperature: float = Field(
        0.1,
        validation_alias="OLLAMA_TEMPERATURE",
        ge=0.0,
        le=1.0,
        description="Temperature for LLM generation (lower = more deterministic)"
    )

    ollama_max_tokens: int = Field(
        256,
        validation_alias="OLLAMA_MAX_TOKENS",
        ge=64,
        le=2048,
        description="Maximum tokens to generate in LLM response"
    )

    ollama_wait_for_model: bool = Field(
        True,
        validation_alias="OLLAMA_WAIT_FOR_MODEL",
        description="Wait for Ollama model loading before returning completion results"
    )

    ollama_model_warmup_prompt: str = Field(
        "Hello",
        validation_alias="OLLAMA_MODEL_WARMUP_PROMPT",
        description="Small warmup prompt used to confirm Ollama model readiness"
    )

    ollama_model_warmup_retries: int = Field(
        10,
        validation_alias="OLLAMA_MODEL_WARMUP_RETRIES",
        ge=1,
        le=20,
        description="Number of warmup attempts to confirm Ollama model readiness"
    )

    ollama_num_predict: int = Field(
        256,
        validation_alias="OLLAMA_NUM_PREDICT",
        ge=64,
        le=2048,
        description="Alternative token limit for Ollama's num_predict parameter"
    )

    ollama_health_check_enabled: bool = Field(
        True,
        validation_alias="OLLAMA_HEALTH_CHECK_ENABLED",
        description="Enable periodic LLM health checks"
    )

    ollama_health_check_timeout: int = Field(
        15,
        validation_alias="OLLAMA_HEALTH_CHECK_TIMEOUT",
        ge=1,
        le=60,
        description="Timeout for health check endpoint in seconds"
    )

    ollama_health_check_interval: int = Field(
        60,
        validation_alias="OLLAMA_HEALTH_CHECK_INTERVAL",
        ge=10,
        description="Interval between health checks in seconds"
    )

    ticket_priority_threshold: float = Field(
        0.65,
        validation_alias="TICKET_PRIORITY_THRESHOLD",
        ge=0.0,
        le=1.0,
        description="Threshold above which tickets are marked high priority"
    )

    escalation_confidence_threshold: float = Field(
        0.55,
        validation_alias="ESCALATION_CONFIDENCE_THRESHOLD",
        ge=0.0,
        le=1.0,
        description="Confidence threshold below which tickets are escalated"
    )

    fallback_to_human: bool = Field(
        True,
        validation_alias="FALLBACK_TO_HUMAN",
        description="Automatically escalate to human when LLM fails"
    )

    fallback_response: str = Field(
        "A human agent will respond to your request shortly. We apologize for the delay.",
        validation_alias="FALLBACK_RESPONSE",
        description="Default response when LLM generation fails"
    )

    log_level: str = Field(
        "INFO",
        validation_alias="LOG_LEVEL",
        description="Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL"
    )

    log_file_path: str = Field(
        "logs/app.log",
        validation_alias="LOG_FILE_PATH",
        description="Path to application log file"
    )
    queue_mode: Literal["local", "redis", "rabbitmq"] = Field(
        "local",
        validation_alias="QUEUE_MODE",
        description="Queue backend mode for async processing"
    )

    cache_ttl_seconds: int = Field(
        300,
        validation_alias="CACHE_TTL_SECONDS",
        gt=0,
        description="Default TTL for cached items in seconds"
    )

    monitoring_enabled: bool = Field(
        True,
        validation_alias="MONITORING_ENABLED",
        description="Enable Prometheus-style metrics endpoint"
    )

    metrics_path: str = Field(
        "/metrics",
        validation_alias="METRICS_PATH",
        description="Endpoint path for Prometheus metrics"
    )

    redis_url: Optional[str] = Field(
        None,
        validation_alias="REDIS_URL",
        description="Redis URL for caching/queueing (if queue_mode != local)"
    )

    api_prefix: str = Field(
        "",
        validation_alias="API_PREFIX",
        description="Optional prefix for all API routes (e.g., '/api/v1')"
    )

    cors_origins: List[str] = Field(
        ["http://localhost:3000", "http://127.0.0.1:3000"],
        validation_alias="CORS_ORIGINS",
        description="Allowed CORS origins for frontend integration"
    )

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  
        protected_namespaces=() 
    )

try:
    settings = Settings()
except Exception as e:
    import sys
    print(f"[CONFIG ERROR] Failed to load settings: {e}", file=sys.stderr)
    print("[CONFIG ERROR] Please ensure .env file exists and contains required variables:", file=sys.stderr)
    print("[CONFIG ERROR] Required: DATABASE_URL, OLLAMA_URL", file=sys.stderr)
    raise
