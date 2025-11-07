from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# Initialize the embedding model (local or Hugging Face hosted)
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Create a FAISS index
dimension = model.get_sentence_embedding_dimension()
index = faiss.IndexFlatL2(dimension)
documents = []

def add_documents(docs):
    global documents
    embeddings = model.encode(docs)
    index.add(np.array(embeddings).astype("float32"))
    documents.extend(docs)

def query_vectorstore(query, top_k=5):
    q_emb = model.encode([query])
    distances, indices = index.search(np.array(q_emb).astype("float32"), top_k)
    results = [documents[i] for i in indices[0]]
    return results

