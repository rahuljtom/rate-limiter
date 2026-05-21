import time
from functools import wraps
import redis

class CircuitBreakerOpen(Exception):
    pass

class RedisCircuitBreaker:
    """
    A Circuit Breaker specifically for Redis interactions.
    If Redis fails continuously, it opens the circuit to prevent 
    cascading failures and slow timeouts in the API.
    """
    def __init__(self, failure_threshold: int = 3, recovery_timeout: int = 30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "CLOSED" # CLOSED, OPEN, HALF_OPEN
        
    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if self.state == "OPEN":
                # Check if it's time to try recovering (HALF_OPEN)
                if time.time() - self.last_failure_time > self.recovery_timeout:
                    self.state = "HALF_OPEN"
                else:
                    raise CircuitBreakerOpen("Redis circuit is OPEN. Fast-failing to protect the system.")
            
            try:
                result = func(*args, **kwargs)
                # If successful and we were HALF_OPEN, the system has recovered!
                if self.state == "HALF_OPEN":
                    self.state = "CLOSED"
                    self.failure_count = 0
                return result
                
            except redis.exceptions.RedisError as e:
                # Only count actual Redis connectivity/execution errors, not our custom exceptions
                self.failure_count += 1
                self.last_failure_time = time.time()
                if self.failure_count >= self.failure_threshold:
                    self.state = "OPEN"
                raise e
        return wrapper

circuit_breaker = RedisCircuitBreaker()
