# Production Readiness Guide

## Architecture overview

This system is designed to run locally and scale with production practices:

- FastAPI backend with asynchronous DB connections
- SQLite for local testing and Postgres-ready SQLAlchemy architecture
- Ollama + Llama 3 integration for AI reply generation
- Local in-memory queue for background processing and optional migration to Redis/RabbitMQ
- Cache layer for repeated classification and priority computation
- Monitoring hooks via metrics and structured logs

## Caching

- `app/services/cache.py` provides a pluggable cache interface.
- `SimpleMemoryCache` is used for local deployments.
- In production, replace or extend with Redis or Memcached for cross-process caching.

## Queue architecture

- `app/services/queue.py` implements an in-memory async queue adapter.
- `app/services/ticket_processor.py` starts a worker to process tickets in the background.
- For production, swap the queue adapter with a Redis-backed or message broker implementation.

## Monitoring hooks

- `app/services/monitoring.py` collects counters and latency histograms.
- `app/main.py` exposes a `/metrics` endpoint with simple text metrics.
- Extend metrics output to Prometheus or OpenTelemetry in production.

## Scaling suggestions

1. Replace SQLite with PostgreSQL in production
2. Use a managed message queue (Redis, RabbitMQ, Kafka)
3. Add distributed caching for shared compute results
4. Deploy FastAPI behind Uvicorn/Gunicorn with multiple workers
5. Configure observability with Prometheus/Grafana and alerting

## Deployment notes

- Use Docker Compose for local development
- Use Kubernetes or ECS for production deployments
- Mount persistent volumes for database and logs
- Add health and readiness probes
- Validate Ollama startup and model availability with `/health/llm`
- Ensure Ollama is reachable before running ticket processing
- Enable `OLLAMA_HEALTH_CHECK_ENABLED=true` in production when Ollama is available
- Use `OLLAMA_HEALTH_CHECK_TIMEOUT` to tune startup polling latency
