from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from loguru import logger
import time

from .auth import verify_api_key
from .vectorstore import add_documents, query_vectorstore
from .cache import get_cache

app = FastAPI(title="Mystic Loops API")

# ----------------------------
# Rate Limiter
# ----------------------------
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# ----------------------------
# CORS Middleware (for UI)
# ----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow UI or external apps
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# Logging
# ----------------------------
logger.add(
    "logs/mystic_loops.log",
    rotation="1 MB",
    format="{time} | {level} | {message}"
)

# ----------------------------
# Input Validation / Prompt Injection Prevention
# ----------------------------
MAX_DOC_LENGTH = 1000

def validate_documents(docs):
    """Validate that documents are strings, not empty, and not too long."""
    if not docs or not isinstance(docs, list):
        raise HTTPException(status_code=400, detail="Provide a list of documents.")
    for i, doc in enumerate(docs):
        if not isinstance(doc, str):
            raise HTTPException(status_code=400, detail=f"Document {i} is not a string.")
        if len(doc.strip()) == 0:
            raise HTTPException(status_code=400, detail=f"Document {i} is empty.")
        if len(doc) > MAX_DOC_LENGTH:
            raise HTTPException(status_code=400, detail=f"Document {i} exceeds max length.")
    return docs

# ----------------------------
# Add initial documents
# ----------------------------
add_documents([
    "The cat sat on the mat.",
    "Python is a programming language.",
    "FastAPI is great for APIs.",
    "FAISS allows fast similarity search."
])

# ----------------------------
# Health Endpoint
# ----------------------------
@app.get("/health")
async def health():
    return {"status": "ok"}

# ----------------------------
# Query Endpoint
# ----------------------------
@app.get("/query")
@limiter.limit("5/minute")
async def query(q: str, request: Request, api_key: str = Depends(verify_api_key)):
    start = time.time()
    results = query_vectorstore(q, top_k=5)
    duration = time.time() - start
    logger.info(f"Query '{q}' processed in {duration:.3f}s")
    return {"results": results, "latency": duration}

# ----------------------------
# Retrieve Endpoint (Add Documents)
# ----------------------------
@app.post("/retrieve")
@limiter.limit("10/minute")
async def retrieve(request: Request, api_key: str = Depends(verify_api_key)):
    """
    Add new documents to the vector store.
    Expects JSON payload: {"documents": ["doc1", "doc2", ...]}
    """
    data = await request.json()
    docs = data.get("documents", [])

    # Validate documents
    docs = validate_documents(docs)

    # Add to vector store
    add_documents(docs)

    # Clear cache to avoid stale results
    cache = get_cache()
    for key in list(cache.keys()):
        cache.pop(key)

    logger.info(f"Added {len(docs)} documents to the vector store")
    return {"status": "documents added", "count": len(docs)}
