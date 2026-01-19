import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)

class PerformanceMiddleware(BaseHTTPMiddleware):
    """
    Middleware to calculate and log the processing time of each request.
    Adds 'X-Process-Time' header to the response.
    """
    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.perf_counter()
        
        response = await call_next(request)
        
        process_time = time.perf_counter() - start_time
        process_time_ms = process_time * 1000
        
        # Add execution time to response headers
        response.headers["X-Process-Time"] = f"{process_time_ms:.2f}ms"
        
        # Log with specific format for easy parsing/monitoring
        logger.info(
            f"PERFORMANCE: {request.method} {request.url.path} "
            f"- Status: {response.status_code} "
            f"- Time: {process_time_ms:.2f}ms"
        )
        
        return response
