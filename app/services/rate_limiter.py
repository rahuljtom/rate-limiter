import os
import time
import uuid
import redis

# Connect to Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

class RateLimitExceeded(Exception):
    pass

def check_rate_limit(user_id: str, limit: int = 5, window_seconds: int = 60) -> dict:
    """
    Sliding window rate limiter using Redis Sorted Sets.
    Returns a dict with rate limit status.
    Raises RateLimitExceeded if the limit is breached.
    """
    key = f"rate_limit:{user_id}"
    now = time.time()
    window_start = now - window_seconds
    
    # We use a pipeline to execute multiple Redis commands atomically
    pipeline = redis_client.pipeline()
    
    # 1. Remove timestamps older than our sliding window
    pipeline.zremrangebyscore(key, 0, window_start)
    
    # 2. Add the current request's timestamp
    # We use UUID to ensure uniqueness if multiple requests happen at the exact same millisecond
    pipeline.zadd(key, {f"{now}-{uuid.uuid4()}": now})
    
    # 3. Count how many requests are in the current window
    pipeline.zcard(key)
    
    # 4. Set an expiry on the key so it automatically cleans up after the window passes
    pipeline.expire(key, window_seconds)
    
    results = pipeline.execute()
    
    # results[2] corresponds to the result of pipeline.zcard(key)
    current_count = results[2]
    
    if current_count > limit:
        raise RateLimitExceeded("Rate limit exceeded")
        
    return {
        "limit": limit,
        "remaining": limit - current_count,
        "window_seconds": window_seconds
    }

def get_rate_limit_status(user_id: str, limit: int = 5, window_seconds: int = 60) -> dict:
    """
    Check current rate limit status without incrementing the counter.
    """
    key = f"rate_limit:{user_id}"
    now = time.time()
    window_start = now - window_seconds
    
    pipeline = redis_client.pipeline()
    pipeline.zremrangebyscore(key, 0, window_start)
    pipeline.zcard(key)
    results = pipeline.execute()
    
    current_count = results[1]
    
    return {
        "limit": limit,
        "remaining": max(0, limit - current_count),
        "window_seconds": window_seconds
    }
