# performance_test.py

import requests
import time
import numpy as np

API_URL = "http://127.0.0.1:8000/query"

import os

API_KEY = os.getenv("API_KEY")


queries = [
    "Python programming",
    "FastAPI tutorial",
    "FAISS similarity search",
    "Cat on the mat",
]

latencies = []

# Benchmark
print("Running benchmark...")
for _ in range(50):  # number of requests per query
    for q in queries:
        start = time.time()
        response = requests.get(API_URL, params={"q": q}, headers={"x-api-key": API_KEY})
        duration = time.time() - start
        latencies.append(duration)
        if response.status_code != 200:
            print(f"Error: {response.json()}")

latencies = np.array(latencies)
print(f"Total requests: {len(latencies)}")
print(f"p50 latency: {np.percentile(latencies, 50)*1000:.2f} ms")
print(f"p95 latency: {np.percentile(latencies, 95)*1000:.2f} ms")
print(f"Average latency: {latencies.mean()*1000:.2f} ms")

