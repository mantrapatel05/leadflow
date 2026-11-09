from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "LeadFlow API"
    app_version: str = "0.1.0"
    app_description: str = (
        "Real-time Meta Lead Ads processing system"
    )
    environment: str = "development"
    debug: bool = True
    api_prefix: str = "/api/v1"
    database_url: str = (
        "postgresql+psycopg://leadflow:leadflow123@localhost:5432/leadflow"
    )
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_timeout: int = 30
    db_pool_recycle: int = 1800
    meta_verify_token: str = ""
    meta_app_secret: str = ""
    meta_page_access_token: str = ""
    meta_graph_api_version: str = "v27.0"
    meta_api_timeout: float = 15.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
