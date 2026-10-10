import os
import httpx

base = os.getenv("BASE_URL", "http://localhost:8000")
api_key = os.getenv("APP_API_KEY", "change-me")

response = httpx.get(f"{base}/health/live", timeout=10)
response.raise_for_status()
print("live:", response.json())

response = httpx.get(
    f"{base}/health/ready",
    headers={"X-API-Key": api_key, "X-Tenant-ID": "smoke"},
    timeout=30,
)
response.raise_for_status()
print("ready:", response.json())
print("Smoke test passed.")
