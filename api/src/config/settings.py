from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "CRUD API"
    app_version: str = "1.0.0"
    debug: bool = False

    # Database
    db_host: str = "localhost"
    db_port: int = 3306
    db_user: str = "admin"
    db_password: str = ""
    db_name: str = "cruddb"
    db_pool_min_size: int = 1
    db_pool_max_size: int = 10

    # AWS
    aws_region: str = "us-east-1"
    sqs_queue_url: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
