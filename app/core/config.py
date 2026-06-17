from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Email Generator"
    environment: str = "development"
    secret_key: str = Field("change-this-secret-key-before-production", min_length=16)
    access_token_expire_minutes: int = 1440
    database_url: str = "sqlite:///./ai_email_generator.db"
    allowed_origins: str = "http://localhost:8000,http://127.0.0.1:8000"
    ai_provider: str = "openai"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    rate_limit: str = "20/minute"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.allowed_origins.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
