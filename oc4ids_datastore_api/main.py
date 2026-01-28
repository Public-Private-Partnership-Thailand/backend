from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
import logging
import os

# Try loading .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from oc4ids_datastore_api.controllers import router
from oc4ids_datastore_api.exceptions import validation_exception_handler, global_exception_handler
from oc4ids_datastore_api.middleware import PerformanceMiddleware

app = FastAPI(
    title="OC4IDS Datastore API",
    version="1.0.0",
    description="Professional grade API for OC4IDS project management."
)

# Register Exception Handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# Add Middleware
app.add_middleware(PerformanceMiddleware)


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# CORS configuration
origins = [
    "http://127.0.0.1:3000",
    "http://localhost:3000",
    "http://127.0.0.1:8080",
    "http://localhost:8080",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Router with Versioning
app.include_router(router, prefix="/api/v1", tags=["Projects"])

