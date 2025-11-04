# main.py
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from slowapi import Limiter
from slowapi.util import get_remote_address
from jose import jwt, JWTError
from loguru import logger
import time, os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Mystic Loops API")

# Rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# JWT secret
SECRET_KEY = os.getenv("SECRET_KEY", "test_secret")
security = HTTPBearer()

@app.get("/")
@limiter.limit("5/minute")
def home(request: Request):
    return {"message": "Welcome to Mystic Loops!"}

@app.get("/secure")
@limiter.limit("3/minute")
def secure_endpoint(request: Request, token: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=["HS256"])
    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid or expired token")
    logger.info(f"Authorized access by {payload['sub']}")
    return {"user": payload["sub"], "status": "Access granted"}

@app.post("/login")
def login(username: str):
    payload = {"sub": username, "iat": int(time.time())}
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    logger.info(f"User {username} logged in")
    return {"access_token": token}
