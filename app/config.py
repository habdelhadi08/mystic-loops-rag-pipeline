from sentence_transformers import SentenceTransformer
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")
JWT_SECRET = os.getenv("JWT_SECRET")

# Initialize the model once, using the key from .env
model = SentenceTransformer("all-MiniLM-L6-v2", use_auth_token=API_KEY)
