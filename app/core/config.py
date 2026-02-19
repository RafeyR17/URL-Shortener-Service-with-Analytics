from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

class Settings(BaseSettings):
    PROJECT_NAME: str = "Modern URL Shortener"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    DATABASE_URL: str = "sqlite+aiosqlite:///./url_shortener.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    BASE_URL: str = "http://localhost:8000"
    
    # Rate limiting
    RATE_LIMIT_SHORTEN: str = "10/minute"
    
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()
