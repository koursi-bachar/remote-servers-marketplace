from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict


class Settings(BaseSettings):
    """
    This class defines every setting our backend needs.
    Pydantic automatically loads them from the environment (such as Github secrets),
    .env files, or Docker env vars. This way, we avoid hard-coded secrets and keep configuration centralized.
    """
    #Let Pydantic handle environment variable loading.
    model_config = ConfigDict(
        env_file=".env",        #works for local dev
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True
    )

    #Environment name (optional)
    ENV: str = Field(default="local")

    #Full connection string for Postgres (or whichever DB is in use).
    #Example: postgres://user:pass@host:5432/db
    DATABASE_URL: str | None = None
    TEST_DATABASE_URL: str | None = None

    #Supabase Auth vars
    SUPABASE_URL: str | None = None
    SUPABASE_ANON_KEY: str | None = None
    SUPABASE_JWT_SECRET: str | None = None

    #Useful for Docker-based Postgres
    POSTGRES_DB: str | None = None
    POSTGRES_USER: str | None = None
    POSTGRES_PASSWORD: str | None = None


settings = Settings()