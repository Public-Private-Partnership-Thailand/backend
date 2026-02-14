from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.requests import Request
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY
import logging

# Define global exception handlers
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Override default validation error to provide a standard error format.
    """
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": "error",
            "code": "VALIDATION_ERROR",
            "message": "Invalid input data",
            "details": exc.errors(),
        },
    )

async def global_exception_handler(request: Request, exc: Exception):
    """
    Catch-all for unexpected errors.
    """
    logging.error(f"Global exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred.",
            "detail": str(exc),
            "timestamp": str(logging.Formatter.formatTime(logging.Formatter(None), record=logging.LogRecord(None, None, "", 0, "", (), None))),
        },
    )

router = APIRouter()
