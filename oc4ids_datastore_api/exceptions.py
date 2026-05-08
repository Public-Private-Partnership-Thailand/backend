import logging

from fastapi import APIRouter
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.requests import Request
from starlette.status import HTTP_422_UNPROCESSABLE_CONTENT

from oc4ids_datastore_api.utils import utcnow_naive


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            "status": "error",
            "code": "VALIDATION_ERROR",
            "message": "Invalid input data",
            "details": exc.errors(),
        },
    )


async def global_exception_handler(request: Request, exc: Exception):
    logging.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred.",
            "timestamp": utcnow_naive().isoformat(),
        },
    )


router = APIRouter()
