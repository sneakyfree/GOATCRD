"""
GOATCRD Configuration Settings
Environment-based configuration with Pydantic Settings
"""
from functools import lru_cache
from typing import Literal

from pydantic import Field, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    # Application
    app_name: str = "GOATCRD"
    app_version: str = "0.1.0"
    debug: bool = False
    environment: Literal["development", "staging", "production"] = "development"
    
    # API
    api_prefix: str = "/api/v1"
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    
    # Database
    database_url: PostgresDsn = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/goatcrd"
    )
    database_pool_size: int = 10
    database_max_overflow: int = 20
    
    # Redis
    redis_url: RedisDsn = Field(default="redis://localhost:6379/0")
    
    # Security
    secret_key: str = Field(default="CHANGE_ME_IN_PRODUCTION_USE_SECURE_KEY")
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    algorithm: str = "HS256"
    
    # Audit
    audit_retention_days: int = 2555  # 7 years default
    
    # Data Provenance
    default_confidence_cap: int = 100
    unknown_field_confidence_cap: int = 50
    contradiction_confidence_cap: int = 60


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
