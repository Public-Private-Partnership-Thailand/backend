# oc4ids_datastore_api/routers/__init__.py
from fastapi import APIRouter
from oc4ids_datastore_api.routers import projects, dashboard, upload, reference, risk

api_router = APIRouter()

api_router.include_router(projects.router,   prefix="/projects",     tags=["Projects"])
api_router.include_router(dashboard.router,  prefix="",              tags=["Dashboard"])
api_router.include_router(upload.router,     prefix="",              tags=["Upload"])
api_router.include_router(reference.router,  prefix="",              tags=["Reference Data"])
api_router.include_router(risk.router,       prefix="",              tags=["Risk Analysis"])

__all__ = ["api_router"]
