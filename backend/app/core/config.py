from pydantic_settings import BaseSettings
from typing import ClassVar, List
import json
import os


class Settings(BaseSettings):
    PROJECT_NAME: str = "FairMirror"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./fairmirror.db"
    )

    MILVUS_HOST: str = os.getenv("MILVUS_HOST", "localhost")
    MILVUS_PORT: int = int(os.getenv("MILVUS_PORT", "19530"))

    SECRET_KEY: str = os.getenv("SECRET_KEY", "fairmirror-local-dev-secret")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    CORS_ORIGINS: str = os.getenv(
        "CORS_ORIGINS",
        "http://localhost,http://localhost:3000,http://localhost:8000",
    )

    @property
    def cors_origins_list(self) -> List[str]:
        value = self.CORS_ORIGINS.strip()
        if not value:
            return []
        if value.startswith("["):
            return json.loads(value)
        return [origin.strip() for origin in value.split(",") if origin.strip()]

    MODEL_PATH: str = os.getenv("MODEL_PATH", "./models")
    BIAS_MODEL_NAME: str = "roberta-bias-classifier"
    ADVERSARIAL_MODEL_NAME: str = "adversarial-debiasing"

    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() in {"1", "true", "yes", "on"}

    DEVELOPMENT_SECRET_KEYS: ClassVar[set] = {
        "fairmirror-local-dev-secret",
        "fairmirror-dev-secret-change-me",
        "your-secret-key-change-in-production",
        "replace-with-at-least-32-random-characters",
        "change-me",
        "secret",
    }

    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() in {"production", "prod"}

    def validate_runtime_settings(self) -> None:
        if not self.is_production():
            return

        errors: List[str] = []
        if self.DEBUG:
            errors.append("DEBUG must be disabled in production")
        if not self.SECRET_KEY or self.SECRET_KEY in self.DEVELOPMENT_SECRET_KEYS or len(self.SECRET_KEY) < 32:
            errors.append("SECRET_KEY must be replaced with a strong production secret")
        if self.DATABASE_URL.startswith("sqlite://"):
            errors.append("DATABASE_URL must not use SQLite in production")
        cors_origins = self.cors_origins_list
        if not cors_origins or "*" in cors_origins:
            errors.append("CORS_ORIGINS must explicitly list trusted origins in production")
        if any(origin.startswith("http://localhost") for origin in cors_origins):
            errors.append("CORS_ORIGINS must not include localhost in production")

        if errors:
            raise ValueError("Invalid production settings: " + "; ".join(errors))

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
settings.validate_runtime_settings()
