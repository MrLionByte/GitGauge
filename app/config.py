from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database Configuration
    DATABASE_URL: str
    
    # GitHub Configuration
    GITHUB_TOKEN: Optional[str] = None
    GITHUB_RATE_LIMIT: int = 100
    GITHUB_TIMEOUT: int = 30

    # AI Configuration
    AI_API_KEY: Optional[str] = None
    AI_MODEL: str = "gpt-3.5-turbo"
    AI_MAX_TOKENS: int = 4096
    AI_TIMEOUT: int = 60
    
    # Redis Configuration (Optional for Celery)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Application Configuration
    APP_NAME: str = "GitGauge"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 15
    RATE_LIMIT_PER_HOUR: int = 100

    # Logger Setup
    LOGTAIL_TOKEN: str
    
    DISCORD_WEBHOOK_URL:str
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()
