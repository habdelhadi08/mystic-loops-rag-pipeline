# main.py

from fastapi import FastAPI, Depends, HTTPException, Response, Request, Body, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.api_key import APIKeyHeader, APIKey
from slowapi import Limiter
from slowapi.util import get_remote_address
from loguru import logger
from pydantic import BaseModel
from typing import List
import time

from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from .vectorstore import add_documents, query_vectorstore
from .cache import get_cache, set_cache
from .observability import log_request, record_metrics, generate_request_id
from .config import API_KEY

# --------------------------
# FastAPI App
# --------------------------
app = FastAPI(title="Mystic Loops API")

# --------------------------
# Rate Limiter
# --------------------------
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# --------------------------
# CORS
# --------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------
# Logging
# --------------------------
logger.add(
    "logs/mystic_loops.log",
    rotation="1 MB",
    format="{time} | {level} | {message}"
)

# --------------------------
# Security (Swagger “Authorize”)
# --------------------------
api_key_header = APIKeyHeader(name="x-api-key", auto_error=True)

async def get_api_key(api_key_header: str = Security(api_key_header)) -> str:
    if api_key_header != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized API Key")
    return api_key_header

# --------------------------
# Request Model
# --------------------------
class RetrieveRequest(BaseModel):
    documents: List[str]

# --------------------------
# Startup: Preload Documents
# --------------------------
@app.on_event("startup")
async def startup_event():
    try:
        await add_documents([
            "The cat sat on the mat.",
            "Python is a programming language.",
            "FastAPI is great for APIs.",
            "FAISS allows fast similarity search.",
            "Data science is the field of extracting knowledge from data.",
            "Machine learning can be supervised or unsupervised.",
            "Neural networks are inspired by the human brain.",
            "Pandas and NumPy are essential Python libraries for data analysis.",
            "SQL is used to query relational databases.",
            "Docker allows containerization of applications."
        ])
        logger.info("Preloaded default documents.")
    except Exception as e:
        logger.error(f"Startup preload failed: {e}")

# --------------------------
# Health Check
# --------------------------
@app.get("/health")
async def health():
    return {"status": "ok"}

# --------------------------
# Prometheus Metrics Endpoint
# --------------------------
@app.get("/metrics")
async def metrics():
    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

# --------------------------
# Retrieve Endpoint
# --------------------------
@app.post("/retrieve")
@limiter.limit("10/minute")
async def retrieve(
    request: Request,
    body: RetrieveRequest = Body(...),
    api_key: APIKey = Depends(get_api_key)
):
    start_time = time.time()
    request_id = generate_request_id()

    try:
        documents = body.documents

        if not documents:
            raise HTTPException(status_code=400, detail="Provide a list of documents.")

        await add_documents(documents)

        latency_ms = (time.time() - start_time) * 1000

        log_request(
            request_id=request_id,
            endpoint="/retrieve",
            method="POST",
            status_code=200,
            latency_ms=latency_ms,
            api_key=api_key
        )

        record_metrics(
            endpoint="/retrieve",
            method="POST",
            status_code=200,
            latency_seconds=latency_ms / 1000
        )

        return {
            "status": "documents added",
            "count": len(documents),
            "latency_ms": round(latency_ms, 2),
            "request_id": request_id
        }

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to add documents")

# --------------------------
# Query Endpoint
# --------------------------
@app.get("/query")
@limiter.limit("500/minute")
async def query(
    request: Request,
    q: str,
    api_key: APIKey = Depends(get_api_key)
):
    start_time = time.time()
    request_id = generate_request_id()

    try:
        # Cache check
        cached_result = get_cache(q)
        if cached_result:
            latency_ms = (time.time() - start_time) * 1000
            return {
                "results": cached_result,
                "latency_ms": round(latency_ms, 2),
                "request_id": request_id,
                "cached": True
            }

        # Vector search
        results = await query_vectorstore(q, top_k=5)

        # Cache result
        set_cache(q, results)

        latency_ms = (time.time() - start_time) * 1000

        log_request(
            request_id=request_id,
            endpoint="/query",
            method="GET",
            status_code=200,
            latency_ms=latency_ms,
            api_key=api_key
        )

        record_metrics(
            endpoint="/query",
            method="GET",
            status_code=200,
            latency_seconds=latency_ms / 1000
        )

        return {
            "results": results,
            "latency_ms": round(latency_ms, 2),
            "request_id": request_id,
            "cached": False
        }

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")