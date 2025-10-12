"""
═══════════════════════════════════════════════════════════════════════════
                                 CONFIG.PY
         APPLICATION CONFIGURATION SETTINGS - MANAGES API KEYS AND
              ENVIRONMENT VARIABLES USING PYDANTIC SETTINGS

FUNCTIONS:
    get_settings() -> RETURNS CACHED SETTINGS INSTANCE
═══════════════════════════════════════════════════════════════════════════
"""

from pydantic_settings import BaseSettings  # type: ignore
from functools import lru_cache

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    GEMINI_API_KEY: str
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def openai_api_key(self) -> str:
        return self.OPENAI_API_KEY
    
    @property
    def gemini_api_key(self) -> str:
        return self.GEMINI_API_KEY

@lru_cache()
def get_settings():
    return Settings()
