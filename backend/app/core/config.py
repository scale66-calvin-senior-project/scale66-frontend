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
    # Application settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True
    output_dir: str = "./output"
    environment: str = "development"
    
    # Supabase configuration
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None  # Anon key (respects RLS)
    supabase_service_key: Optional[str] = None  # Service role key (bypasses RLS)
    supabase_jwt_secret: Optional[str] = None  # For JWT verification
    
    # AI Services
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    openai_model: str = "gpt-4"
    gemini_model: str = "gemini-2.5-flash-image"
    
    # Email service (Resend)
    resend_api_key: Optional[str] = None
    resend_audience_id: Optional[str] = None
    
    # Storage (AWS S3 - optional, if not using Supabase Storage)
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    s3_bucket_name: Optional[str] = None
    s3_region: str = "us-east-1"
    
    # Cloudinary (alternative storage - optional)
    cloudinary_cloud_name: Optional[str] = None
    cloudinary_api_key: Optional[str] = None
    cloudinary_api_secret: Optional[str] = None
    
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
    
    # Optional: Background jobs
    redis_url: Optional[str] = None
    celery_broker_url: Optional[str] = None
    
    # Optional: Monitoring
    sentry_dsn: Optional[str] = None

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