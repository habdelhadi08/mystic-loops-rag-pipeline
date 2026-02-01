# Mystic Loops – Production-Ready RAG API
## Task
### Overview
**Mystic Loops** is a hardened Retrieval-Augmented Generation (RAG) backend built with **FastAPI**.  
The project moves beyond “it works” and focuses on **production readiness**: security, rate limiting, caching, observability, and measurable performance.

The API allows:
- Secure document ingestion into a vector store
- Low-latency semantic retrieval
- Metrics and structured logs for monitoring and debugging

---
## Description

Mystic Loops is a hardened backend API built using FastAPI that supports semantic document retrieval using vector embeddings.
The project emphasizes production-readiness by integrating authentication, request throttling, caching, structured logging, and monitoring.

Key objectives include:

- Securing API access using API keys

- Reducing retrieval latency with FAISS and caching

- Providing metrics and logs for debugging and monitoring

- Ensuring reliability through validation and defensive error handling

## Architecture

```text
Client
  |
  |  API Key + Rate Limiting
  v
FastAPI
  ├── /retrieve   → Add documents
  ├── /query      → Semantic retrieval (cached)
  ├── /health     → Health check
  ├── /metrics    → Prometheus metrics
  |
  ├── FAISS Vector Store
  ├── In-Memory Cache
  ├── Loguru Structured Logs
  └── Prometheus Metrics
```

---

## Features Implemented

### Security
- API key authentication (`x-api-key` header)
- Unauthorized access returns **401**
- Secrets stored in environment variables
- No secrets committed to GitHub

### Rate Limiting
- Implemented using **slowapi**
- `/retrieve`: **10 requests/minute**
- `/query`: **500 requests/minute**
- Rate-limit violations return **429**

### Performance
- FAISS vector similarity search
- In-memory query cache
- Reduced latency on repeated queries
- Warm-cache p50 under **500ms**

### Observability
- Structured JSON logs with **Loguru**
- Correlation IDs per request
- Prometheus metrics:
  - Request count
  - Request latency histograms
- `/metrics` endpoint enabled

### Reliability
- Input validation with **Pydantic**
- Defensive error handling
- Safe defaults and explicit failures

---

## API Endpoints

### Health Check
```http
GET /health
```

Response:
```json
{
  "status": "ok"
}
```

---

### Add Documents
```http
POST /retrieve
```

Headers:
```text
x-api-key: YOUR_API_KEY
Content-Type: application/json
```

Body:
```json
{
  "documents": [
    "FastAPI is a modern Python web framework.",
    "FAISS enables fast vector similarity search."
  ]
}
```

Response:
```json
{
  "status": "documents added",
  "count": 2,
  "latency_ms": 12.4,
  "request_id": "uuid"
}
```

---

### Query Vector Store
```http
GET /query?q=What is FastAPI?
```

Headers:
```text
x-api-key: YOUR_API_KEY
```

Response:
```json
{
  "results": [...],
  "latency_ms": 184.2,
  "request_id": "uuid",
  "cached": false
}
```

---

### Metrics (Prometheus)
```http
GET /metrics
```

Example output:
```text
# HELP requests_total Total API requests
# TYPE requests_total counter
requests_total{endpoint="/query",method="GET",status="200"} 1.0

# HELP request_latency_seconds Request latency
# TYPE request_latency_seconds histogram
request_latency_seconds_bucket{endpoint="/query",le="0.5"} 1.0
```

---
## Installation

### Requirements
- Python 3.10 or higher
- pip package manager
- Virtual environment (recommended)


## Usage 

### Environment Setup

### Python Version
Python 3.10+

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file (do not commit it):

```bash
API_KEY=your_api_key_here
```

Example `.env.example`:
```bash
API_KEY=example_key
```

---

## Running the Application
```bash
uvicorn app.main:app --reload
```

Application URL:
```text
http://127.0.0.1:8000
```

Swagger Docs:
```text
http://127.0.0.1:8000/docs
```

---

## Logging

Logs are written to:
```text
logs/mystic_loops.log
```

Each log entry includes:
- request_id
- endpoint
- method
- status
- latency_ms

---

## Performance Evidence
- Warm-cache retrieval p50 < 500ms
- Reduced latency for repeated queries
- Metrics visible via `/metrics`

---

## Project Structure
```text
mystic-loops/
├── app/    
│   ├── main.py
│   ├── vectorstore.py
│   ├── cache.py
│   ├── auth.py
│   ├── observability.py
│   └── config.py
│
├── logs/
│   └── mystic_loops.log
│
├── performance-tests/
├── .env.example
├── README.md
└── requirements.txt
```

---

## Acceptance Criteria Checklist
- [x] Authenticated endpoints
- [x] Rate-limited access
- [x] Cached retrieval
- [x] Structured logging
- [x] Prometheus metrics
- [x] No secrets committed
- [x] Production-ready API

---

## Author

Heba Abdelhadi  
- Season 03 – AI Application Developer  
- Qwasar Valley

## The Core Team


<span><i>Made at <a href='https://qwasar.io'>Qwasar SV -- Software Engineering School</a></i></span>
<span><img alt='Qwasar SV -- Software Engineering School's Logo' src='https://storage.googleapis.com/qwasar-public/qwasar-logo_50x50.png' width='20px' /></span>
