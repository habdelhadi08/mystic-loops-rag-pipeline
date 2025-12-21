import time
import uuid
from loguru import logger
from prometheus_client import Counter, Histogram

# Define metrics only once here
REQUEST_COUNT = Counter(
    "requests_total",
    "Total API requests",
    ["endpoint", "method", "status"]
)
REQUEST_LATENCY = Histogram(
    "request_latency_seconds",
    "Request latency",
    ["endpoint"]
)

# Generate request IDs
def generate_request_id() -> str:
    return str(uuid.uuid4())

# Structured logging
def log_request(*, request_id: str, endpoint: str, method: str, status_code: int, latency_ms: float, api_key: str | None = None):
    logger.info({
        "request_id": request_id,
        "endpoint": endpoint,
        "method": method,
        "status": status_code,
        "latency_ms": round(latency_ms, 2),
        "api_key": api_key,
    })

# Record metrics
def record_metrics(*, endpoint: str, method: str, status_code: int, latency_seconds: float):
    REQUEST_COUNT.labels(endpoint=endpoint, method=method, status=str(status_code)).inc()
    REQUEST_LATENCY.labels(endpoint=endpoint).observe(latency_seconds)
