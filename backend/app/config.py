import os
import secrets
import socket
from typing import List, Union, Optional

from pydantic import AnyHttpUrl, EmailStr, model_validator, Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8

    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",  
        "http://localhost:8080",
        "http://localhost",
    ]

    @model_validator(mode='before')
    def assemble_cors_origins(cls, values):
        if isinstance(values.get("BACKEND_CORS_ORIGINS"), str):
            values["BACKEND_CORS_ORIGINS"] = [
                i.strip() for i in values["BACKEND_CORS_ORIGINS"].split(",")
            ]
        return values

    PROJECT_NAME: str = "TodoList API"

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """
        Get database URI based on environment.
        For Docker: postgresql://postgres:postgres@postgres/tododb
        For local: postgresql://postgres:postgres@localhost/tododb
        """
        db_uri = os.getenv("SQLALCHEMY_DATABASE_URI", "postgresql://postgres:postgres@postgres/tododb")
        
        if "postgres" in db_uri and not self._is_host_reachable("postgres"):
            return db_uri.replace("@postgres/", "@localhost/")
        return db_uri

    @property
    def REDIS_URL(self) -> str:
        """
        Get Redis URL based on environment.
        For Docker: redis://redis:6379/0
        For local: redis://localhost:6379/0
        """
        redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
        
        if "redis://" in redis_url and not self._is_host_reachable("redis"):
            return redis_url.replace("redis://redis:", "redis://localhost:")
        return redis_url

    @property
    def ELASTICSEARCH_URL(self) -> str:
        """
        Get Elasticsearch URL based on environment.
        For Docker: http://elasticsearch:9200
        For local: http://localhost:9200
        """
        es_url = os.getenv("ELASTICSEARCH_URL", "http://elasticsearch:9200")
        
        if "elasticsearch" in es_url and not self._is_host_reachable("elasticsearch"):
            return es_url.replace("elasticsearch:", "localhost:")
        return es_url

    ELASTICSEARCH_INDEX_PREFIX: str = "todolist_"

    def _is_host_reachable(self, host: str) -> bool:
        """Check if a host is reachable"""
        try:
            socket.gethostbyname(host)
            return True
        except socket.error:
            return False

    class Config:
        case_sensitive = True

settings = Settings() 