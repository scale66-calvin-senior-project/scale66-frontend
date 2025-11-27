"""
Settings Configuration - Centralized environment-driven configuration management.
Loads API keys, model names, server settings, and output paths from environment
variables or .env file with sensible defaults.

Main Components:
    1. Settings class - Pydantic model for type-safe configuration
    2. settings instance - Singleton configuration object used throughout application

Connections:
    - Used by: All services (AnthropicService, GeminiService) and agents for configuration
    - Loads from: .env file or environment variables
    - Provides: API keys, model names, host/port, output directory
"""

import os
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True
    output_dir: str = "./output"
    environment: str = "development"
    
    # Logging configuration
    log_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    log_to_file: bool = True  # Enable file logging
    log_file: str = "./logs/scale66.log"  # Log file path
    log_file_max_bytes: int = 10485760  # 10MB max file size
    log_file_backup_count: int = 5  # Keep 5 backup files
    
    # Local output configuration
    save_local_output: bool = True  # Save generated images locally for debugging
    
    # Supabase configuration
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None  # Anon key (respects RLS)
    supabase_service_key: Optional[str] = None  # Service role key (bypasses RLS)
    supabase_jwt_secret: Optional[str] = None  # For JWT verification
    
    # AI Services
    anthropic_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    anthropic_model: str = "claude-sonnet-4-5"
    
    # Gemini image generation model configuration
    # Supported models:
    #   - gemini-3-pro-image-preview (recommended: highest quality, supports 4K)
    #   - gemini-2.5-flash-image (faster, cost-effective)
    gemini_image_model: str = "gemini-3-pro-image-preview"
    
    # Email service (Resend)
    resend_api_key: Optional[str] = None
    resend_audience_id: Optional[str] = None
    
    # Social Media APIs
    instagram_client_id: Optional[str] = None
    instagram_client_secret: Optional[str] = None
    tiktok_client_key: Optional[str] = None
    tiktok_client_secret: Optional[str] = None
    
    # Stripe payment processing
    stripe_secret_key: Optional[str] = None
    stripe_webhook_secret: Optional[str] = None
    
    # CORS origins (comma-separated in .env)
    cors_origins: str = "http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
    def get_cors_origins(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]


settings = Settings()
os.makedirs(settings.output_dir, exist_ok=True)