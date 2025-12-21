import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from .cache import get_cache, set_cache, clear_cache
import asyncio
from loguru import logger
from .config import API_KEY

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2", use_auth_token=API_KEY)

# FAISS HNSW Index
EMBED_DIM = model.get_sentence_embedding_dimension()
index = faiss.IndexHNSWFlat(EMBED_DIM, 32)
index.hnsw.efConstruction = 200
index.hnsw.efSearch = 50

# Store documents in parallel list
documents = []

# Lock for async safety
index_lock = asyncio.Lock()

# Max document length
MAX_DOC_LENGTH = 4000

def validate_documents(docs):
    return [d for d in docs if isinstance(d, str) and 0 < len(d) <= MAX_DOC_LENGTH]

async def add_documents(docs: list[str]):
    docs = validate_documents(docs)
    if not docs:
        logger.warning("No valid documents to add")
        return

    embeddings = model.encode(docs, convert_to_numpy=True, show_progress_bar=False)

    async with index_lock:
        index.add(embeddings)
        documents.extend(docs)
        clear_cache()

    logger.info(f"Added {len(docs)} documents to vector store. Cache cleared.")

async def query_vectorstore(query: str, top_k: int = 5):
    async with index_lock:
        cached = get_cache(query)
        if cached:
            logger.info(f"Cache hit for query: '{query}'")
            return cached

    embedding = model.encode([query], convert_to_numpy=True)

    async with index_lock:
        D, I = index.search(embedding, top_k)
        results = [documents[i] for i in I[0] if i < len(documents)]

    set_cache(query, results)
    logger.info(f"Cache set for query: '{query}'")
    return results



