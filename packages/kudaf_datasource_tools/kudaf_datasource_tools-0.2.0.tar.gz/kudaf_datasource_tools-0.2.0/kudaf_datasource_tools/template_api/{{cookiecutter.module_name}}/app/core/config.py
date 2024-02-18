import os
from typing import Optional
from pydantic import DirectoryPath, AnyHttpUrl, BaseSettings, HttpUrl, validator


class Settings(BaseSettings):
    PROJECT_NAME: str = "{{ cookiecutter.project_name }}"
    BASE_PROJECT_DIR: DirectoryPath = os.path.join(os.getcwd(), 'app')
    FILES_PATH: DirectoryPath = os.path.join(os.getcwd(), 'files') 
    METADATA_PATH: DirectoryPath = os.path.join(os.getcwd(), 'metadata') 
    API_STR: str = "/api"
    SERVER_NAME: str = "localhost"
    SERVER_HOST: AnyHttpUrl = "http://127.0.0.1"

    # KUDAF stuff
    DATASOURCE_NAME: str = "{{ cookiecutter.datasource_name }}"
    DATASOURCE_ID: str = "{{ cookiecutter.datasource_id }}"
    KUDAF_CORE_SERVER_PERMISSIONS_URL: HttpUrl = "https://kudaf-core.paas2.uninett.no/api/v1/permissions/"
    KUDAF_DATASOURCE_AUDIENCE: str = "https://n.feide.no/datasources/" + DATASOURCE_ID
    KUDAF_CORE_AUDIENCE = "https://n.feide.no/datasources/c25e267b-ffe0-4fa4-a67f-da2be29c3f0e"
    DATAPORTEN_URL: HttpUrl = "https://auth.dataporten.no"
    VARIABLE_MAPPINGS: dict = {{ cookiecutter.variable_mappings }}
    
    SENTRY_DSN: HttpUrl  = "http://127.0.0.1"

    @validator("SENTRY_DSN", pre=True)
    def sentry_dsn_can_be_blank(cls, v: str) -> Optional[str]:
        if len(v) == 0:
            return None
        return v

    class Config:
        case_sensitive = True


settings = Settings()
