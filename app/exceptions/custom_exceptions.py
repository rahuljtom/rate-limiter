from fastapi import status

class AppException(Exception):
    def __init__(self, error: str, message: str, status_code: int, details: dict = None):
        self.error = error
        self.message = message
        self.status_code = status_code
        self.details = details or {}

class RateLimitExceeded(AppException):
    def __init__(self, details=None):
        super().__init__(
            error="rate_limit_exceeded",
            message="Too many requests",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details=details
        )

class InvalidToken(AppException):
    def __init__(self):
        super().__init__(
            error="invalid_token",
            message="Invalid or expired token",
            status_code=status.HTTP_401_UNAUTHORIZED
        )

class BadRequest(AppException):
    def __init__(self, message="Bad request", details=None):
        super().__init__(
            error="bad_request",
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details
        )
