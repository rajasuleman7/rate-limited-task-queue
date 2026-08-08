
import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    jwt_secret_key:        str = "dev-secret-change-in-production-min-32-chars"
    jwt_algorithm:         str = "HS256"
    jwt_expire_minutes:    int = 60
    redis_url:             str = "redis://localhost:6379/0"
    celery_broker_url:     str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"
    rate_limit_default:    int = 30
    rate_limit_premium:    int = 100
    rate_limit_admin:      int = 500
    task_timeout_seconds:  int = 300


@lru_cache
def get_settings() -> Settings:
    return Settings()
