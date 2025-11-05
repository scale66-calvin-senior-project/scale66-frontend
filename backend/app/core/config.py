from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True
    
    # Output Configuration
    output_dir: str = "./output"
    
    # Agent Configuration
    max_slides: int = 20
    min_slides: int = 1
    
    # External API Keys
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    
    # LLM Configuration
    text_generation_provider: str = "openai"  # openai for ChatGPT
    openai_model: str = "gpt-3.5-turbo"  # or gpt-4
    
    # Image Generation
    image_generation_provider: str = "gemini"  # gemini for nanobanana
    gemini_model: str = "gemini-pro-vision"  # or specific nanobanana model
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()

# Ensure output directory exists
os.makedirs(settings.output_dir, exist_ok=True)