"""
Settings Configuration - Centralized environment-driven configuration management.
Loads API keys, model names, server settings, and output paths from environment
variables or .env file with sensible defaults.

Main Components:
    1. Settings class - Pydantic model for type-safe configuration
    2. settings instance - Singleton configuration object used throughout application

Connections:
    - Used by: All services (OpenAIService, GeminiService) and agents for configuration
    - Loads from: .env file or environment variables
    - Provides: API keys, model names, host/port, output directory
"""

import os
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


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