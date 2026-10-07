from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "LegalEase"

    gemini_api_key: str = ""

    gemini_model: str = "gemini-3.8-flash"

    demo_mode: bool = False

    backend_url: str = "http://127.0.0.1:8000"

    max_document_chars: int = 30000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()