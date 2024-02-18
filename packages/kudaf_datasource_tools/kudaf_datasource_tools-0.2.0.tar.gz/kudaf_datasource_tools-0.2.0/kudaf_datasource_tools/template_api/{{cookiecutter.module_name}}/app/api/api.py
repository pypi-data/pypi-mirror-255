from fastapi import APIRouter

from app.api.endpoints import variables, metadata


api_router = APIRouter()
api_router.include_router(variables.router, prefix="/variables", tags=["Kudaf Data"])
api_router.include_router(metadata.router, prefix="/metadata", tags=["Kudaf Metadata"])
