import os 
import json
from typing import Optional
from fastapi import Response, HTTPException, status
from fastapi.logger import logger


def prepend_datasource_name(ds_name: str, var_name: str) -> str:
    """
    Ensures the name of the Datasource is somehow included in
    the variable name, otherwise pre-pends it
    """
    if ds_name.lower() not in var_name.lower():
        return ds_name.upper() + "_" + var_name
    else:
        return var_name


def safe_file_open_w(path:str):
    ''' 
    Open "path" for writing, creating any parent directories as needed.
    '''
    os.makedirs(os.path.dirname(path), exist_ok=True)

    return open(path, 'w', newline='')


def show_error_response(
    response: Optional[Response] = None, 
    status_code: Optional[int] = status.HTTP_400_BAD_REQUEST,
    headers: Optional[dict] = None, 
    detail: Optional[str] = None
    ) -> HTTPException:
    """
    Raise an HTTP exception
    """
    if response is None:
        raise HTTPException(
            status_code=status_code,
            detail=detail,
            headers=headers,
        )
    else:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.json(),
            headers=headers,
        )


def load_json(filepath: str) -> dict:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to open file at {str(filepath)}")
        return []
    