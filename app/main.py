from fastapi import FastAPI, Request, Depends, HTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import asyncio
import time

from .auth import verify_api_key
from .vectorstore import add_documents_async, query_vectorstore_async
from .cache import query_cache

app = FastAPI(title="Mystic Loops API")

# Rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# CORS middleware (for optional UI)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging
logger.add("logs/mystic_loops.log", rotation="1 MB", format="{time} | {level} | {message}")

# Async lock for vectorstore operations
vectorstore_lock = asyncio.Lock()

# Add initial documents at startup (synchronous for simplicity)
async def startup_documents():
    async with vectorstore_lock:
        await add_documents_async([
            "The cat sat on the mat.",
            "Python is a programming language.",
            "FastAPI is great for APIs.",
            "FAISS allows fast similarity search."
        ])

@app.on_event("startup")
async def startup_event():
    await startup_documents()

# Health endpoint
@app.get("/health")
async def health():
    return {"status": "ok"}

# Query endpoint (async + cache)
@app.get("/query")
@limiter.limit("5/minute")
async def query(q: str, request: Request, api_key: str = Depends(verify_api_key)):
    # Check cache first
    if q in query_cache:
        results = query_cache[q]
        logger.info(f"Cache hit for query: '{q}'")
    else:
        start = time.time()
        async with vectorstore_lock:
            results = await query_vectorstore_async(q, top_k=5)
        duration = time.time() - start
        query_cache[q] = results
        logger.info(f"Query '{q}' processed in {duration:.3f}s")
    
    return {"results": results, "latency": 0}  # latency can be added if needed

# Retrieve endpoint (async + safe cache clearing)
@app.post("/retrieve")
@limiter.limit("10/minute")
async def retrieve(request: Request, api_key: str = Depends(verify_api_key)):
    data = await request.json()
    docs = data.get("documents", [])
    if not docs or not isinstance(docs, list):
        raise HTTPException(status_code=400, detail="Provide a list of documents.")

    async with vectorstore_lock:
        await add_documents_async(docs)

        # Clear cache safely
        keys_to_clear = list(query_cache.keys())
        for key in keys_to_clear:
            query_cache.pop(key)

    logger.info(f"Added {len(docs)} documents to the vector store and cleared cache")
    return {"status": "documents added", "count": len(docs)}

