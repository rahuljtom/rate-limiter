import os
import json
import redis
from typing import Optional

# Connect to Redis (reusing the same connection string logic)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

def get_idempotent_response(key: str) -> Optional[dict]:
    """
    Check if a response has already been cached for this unique idempotency key.
    """
    cached = redis_client.get(f"idempotency:{key}")
    if cached:
        return json.loads(cached)
    return None

def save_idempotent_response(key: str, response_data: dict, expire_seconds: int = 86400):
    """
    Save the successful transaction response to Redis for 24 hours (86400 seconds).
    """
    redis_client.set(
        f"idempotency:{key}",
        json.dumps(response_data),
        ex=expire_seconds
    )
