from sentence_transformers import SentenceTransformer
import os
from dotenv import load_dotenv

load_dotenv()

# Environment variables
API_KEY = os.getenv("API_KEY")
JWT_SECRET = os.getenv("JWT_SECRET")

# Load embedding model ONCE (no API key passed)
model = SentenceTransformer("all-MiniLM-L6-v2")