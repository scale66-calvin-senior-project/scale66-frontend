import os
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


# Overview:
# - Purpose: Centralize environment-driven settings for the carousel backend.
# Key Components:
# - Settings: captures API, model, and provider configuration.
# - settings: singleton instance with ensured output directory.


class Settings(BaseSettings):
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True
    output_dir: str = "./output"
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    openai_model: str = "gpt-3.5-turbo"
    gemini_model: str = "gemini-2.5-flash-image"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
os.makedirs(settings.output_dir, exist_ok=True)