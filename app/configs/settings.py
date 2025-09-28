"""Application configuration."""

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    app_name: str = "Voice API"
    app_version: str = "0.1.0"
    app_description: str = "Web service that infers and manages a brand's voice - warmth, seriousness, technicality"
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # API settings
    # api_prefix: str = "/api/v1"
    api_prefix: str = ""

    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5555/voice_api")
    
    # API Keys
    COHERE_API_KEY: str = os.getenv("COHERE_API_KEY", "")
    
    class Config:
        """Configuration settings."""
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
