from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List
import json


class Settings(BaseSettings):
    # App
    APP_NAME: str = "OBA Smart Assistant"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "postgresql://oba_user:oba_password@localhost:5432/oba_db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days
    
    # Google Cloud
    GOOGLE_CLOUD_API_KEY: str = ""
    
    # Gemini API
    GEMINI_API_KEY: str = ""
    
    # Firebase
    FIREBASE_SERVER_KEY: str = ""
    
    # CORS
    ALLOWED_ORIGINS: str = '["http://localhost:3000", "http://localhost:5000", "http://localhost:8000"]'
    
    @property
    def cors_origins(self) -> List[str]:
        return json.loads(self.ALLOWED_ORIGINS)
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()
