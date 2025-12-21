# main.py
from fastapi import FastAPI, Depends, Header, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from loguru import logger
import time
from typing import List
from pydantic import BaseModel
from fastapi import Request

from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from .vectorstore import add_documents, query_vectorstore
from .config import API_KEY
from .observability import log_request, record_metrics, generate_request_id, REQUEST_COUNT, REQUEST_LATENCY
from fastapi import Body

app = FastAPI(title="Mystic Loops API")

# Rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging
logger.add("logs/mystic_loops.log", rotation="1 MB", format="{time} | {level} | {message}")

# --------------------------
# API Key dependency
# --------------------------
def verify_api_key(x_api_key: str = Header(..., description="API Key")):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized API Key")
    return x_api_key

# --------------------------
# Pydantic model for /retrieve
# --------------------------
class RetrieveRequest(BaseModel):
    documents: List[str]

# --------------------------
# Startup: preload documents
# --------------------------
@app.on_event("startup")
async def startup_event():
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

# --------------------------
# Health check
# --------------------------
@app.get("/health")
async def health():
    return {"status": "ok"}

# --------------------------
# Retrieve endpoint
# --------------------------
@app.post("/retrieve")
@limiter.limit("10/minute")
async def retrieve( request: Request,
    body: RetrieveRequest = Body(..., description="List of documents to add"),
    api_key: str = Depends(verify_api_key)
):
    start_time = time.time()
    request_id = generate_request_id()

    documents = body.documents
    if not documents:
        raise HTTPException(status_code=400, detail="Provide a list of documents.")

    await add_documents(documents)
    latency_ms = (time.time() - start_time) * 1000

    # Logging & metrics
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


# --------------------------
# Query endpoint
# --------------------------
from .cache import get_cache, set_cache

@app.get("/query")
@limiter.limit("500/minute")
async def query(request: Request, q: str, api_key: str = Depends(verify_api_key)):
    start_time = time.time()
    request_id = generate_request_id()

    # Check cache first
    cached_result = get_cache(q)
    if cached_result:
        latency_ms = (time.time() - start_time) * 1000
        return {
            "results": cached_result,
            "latency_ms": round(latency_ms, 2),
            "request_id": request_id,
            "cached": True
        }

    # Query vector store
    results = await query_vectorstore(q, top_k=5)

    # Store in cache
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
    record_metrics(endpoint="/query", method="GET", status_code=200, latency_seconds=latency_ms / 1000)

    return {
        "results": results,
        "latency_ms": round(latency_ms, 2),
        "request_id": request_id,
        "cached": False
    }
