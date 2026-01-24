# Mystic Loops – Production-Ready RAG API

## Task Section
The goal of this project is to build a **production-ready RAG API** using FastAPI.  
It focuses on security, performance, observability, and reliability.  
You will implement authenticated endpoints, rate limiting, low-latency semantic retrieval, caching, and structured logging.  
Optional UI support allows human-in-the-loop testing of query results.

---

## Description Section
**Mystic Loops** is a Retrieval-Augmented Generation backend that is hardened for real-world usage.  
It supports secure document ingestion, semantic search with FAISS, caching for repeated queries, and full observability.  
Structured logs and Prometheus metrics allow monitoring latency, errors, and throughput.  
This project moves a working prototype into a scalable and reliable system.

---

## Installation Section
1. Clone the repository:
```bash
git clone git@git.us.qwasar.io:mystic-loops_194641_vz19sz/mystic-loops.git
cd mystic-loops
```
2. Create a virtual environment and activate it:
```bash
python -m venv venv
.\venv\Scripts\activate    # Windows
source venv/bin/activate   # Linux/Mac
```
3. Install dependencies:
```bash
pip install -r requirements.txt
```
4. Create a `.env` file with your API and JWT keys:
```bash
API_KEY=your_api_key_here
SECRET_KEY=super_secret_jwt_key
```

---

## Usage Section
1. Run the FastAPI server:
```bash
uvicorn app.main:app --reload
```
2. Access the API at `http://127.0.0.1:8000`
3. Check Swagger documentation:
```text
http://127.0.0.1:8000/docs
```
4. Example endpoints:
- `POST /retrieve` → add documents
- `GET /query?q=your_query` → perform semantic search
- `GET /health` → health check
- `GET /metrics` → Prometheus metrics
5. Logs are stored in `logs/mystic_loops.log` with structured JSON format.

---

## Qwasar Reference
**Project Author:** Heba Abdelhadi  
**Season:** 03 – AI Application Developer  
**Repository URL:**  
```text
git@git.us.qwasar.io:mystic-loops_194641_vz19sz/mystic-loops.git
```
**This project demonstrates:** production readiness, secure API access, observability, caching, and low-latency retrieval for RAG pipelines.
