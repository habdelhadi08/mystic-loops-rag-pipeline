from fastapi import FastAPI, Request, Depends
from auth import verify_api_key
from cache import query_cache, get_cache, set_cache
from vectorstore import add_documents, query_vectorstore
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import time

app = FastAPI(title="Mystic Loops API")

# Rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# CORS middleware (for UI)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging
logger.add("logs/mystic_loops.log", rotation="1 MB", format="{time} | {level} | {message}")

# Add initial documents
add_documents([
    "The cat sat on the mat.",
    "Python is a programming language.",
    "FastAPI is great for APIs.",
    "FAISS allows fast similarity search."
])

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/query")
@limiter.limit("5/minute")
async def query(q: str, request: Request, api_key: str = Depends(verify_api_key)):
    start = time.time()
    results = query_vectorstore(q, top_k=5)
    duration = time.time() - start
    logger.info(f"Query '{q}' processed in {duration:.3f}s")
    return {"results": results, "latency": duration}

@app.post("/retrieve")
@limiter.limit("10/minute")
async def retrieve(request: Request, api_key: str = Depends(verify_api_key)):
    data = await request.json()
    docs = data.get("documents", [])
    if not docs or not isinstance(docs, list):
        return {"status": "error", "message": "Provide a list of documents."}

    add_documents(docs)

    # Clear cache for stale results
    for key in list(query_cache.keys()):
        query_cache.pop(key)

    logger.info(f"Added {len(docs)} documents to the vector store")
    return {"status": "documents added", "count": len(docs)}
