from fastapi import Request
from fastapi.responses import JSONResponse
from app.exceptions.custom_exceptions import AppException

async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error,
            "message": exc.message,
            "details": exc.details
        }
    )

