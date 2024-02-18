import os 
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.utils.utils import load_json


router = APIRouter()


@router.get("/variables", response_class=JSONResponse)
async def kudaf_datasource_variables_metadata():
    f"""
    Kudaf Variables Metadata for Feide Datasource: {settings.DATASOURCE_NAME}  
    """
    filepath = os.path.join(settings.METADATA_PATH, 'variables_metadata.json')
    metadata = load_json(filepath)

    return metadata


@router.get("/unit-types", response_class=JSONResponse)
async def kudaf_datasource_unit_types_metadata():
    f"""
    Kudaf Unit Types Metadata for Feide Datasource: {settings.DATASOURCE_NAME}  
    """
    filepath = os.path.join(settings.METADATA_PATH, 'unit_types_metadata.json')
    metadata = load_json(filepath)

    return metadata
