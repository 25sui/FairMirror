import os


class Settings:
    app_name: str = os.getenv("APP_NAME", "FairMirror API")
    api_prefix: str = os.getenv("API_PREFIX", "/api/v1")
    cors_origins: list[str] = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://fairmirror:fairmirror@postgres:5432/fairmirror",
    )


settings = Settings()