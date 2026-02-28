import faiss
import numpy as np
import asyncio
from loguru import logger

from .cache import get_cache, set_cache, clear_cache
from .config import model   # <-- import model from config (load once only)

# --------------------------
# FAISS HNSW Index
# --------------------------

EMBED_DIM = model.get_sentence_embedding_dimension()

index = faiss.IndexHNSWFlat(EMBED_DIM, 32)
index.hnsw.efConstruction = 200
index.hnsw.efSearch = 50

documents = []

index_lock = asyncio.Lock()

MAX_DOC_LENGTH = 4000


# --------------------------
# Validation
# --------------------------

def validate_documents(docs):
    return [
        d for d in docs
        if isinstance(d, str) and 0 < len(d) <= MAX_DOC_LENGTH
    ]


# --------------------------
# Add Documents
# --------------------------

async def add_documents(docs: list[str]):
    docs = validate_documents(docs)

    if not docs:
        logger.warning("No valid documents to add")
        return

    try:
        embeddings = model.encode(
            docs,
            convert_to_numpy=True,
            show_progress_bar=False
        )

        async with index_lock:
            index.add(embeddings)
            documents.extend(docs)
            clear_cache()

        logger.info(f"Added {len(docs)} documents to vector store. Cache cleared.")

    except Exception as e:
        logger.error(f"Error adding documents: {e}")
        raise


# --------------------------
# Query
# --------------------------

async def query_vectorstore(query: str, top_k: int = 5):
    if not isinstance(query, str) or not query.strip():
        raise ValueError("Query must be a non-empty string")

    try:
        async with index_lock:
            cached = get_cache(query)
            if cached:
                logger.info(f"Cache hit for query: '{query}'")
                return cached

        embedding = model.encode(
            [query],
            convert_to_numpy=True,
            show_progress_bar=False
        )

        async with index_lock:
            D, I = index.search(embedding, top_k)
            results = [
                documents[i]
                for i in I[0]
                if i < len(documents)
            ]

        set_cache(query, results)
        logger.info(f"Cache set for query: '{query}'")

        return results

    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise

