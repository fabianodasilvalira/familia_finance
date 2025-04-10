import os
from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any, List

class Settings(BaseSettings):
    PROJECT_NAME: str = "Family Finance Manager"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/familyfinance")
    
    # Budget thresholds for notifications
    BUDGET_WARNING_THRESHOLD: float = 0.7  # 70% of budget used
    BUDGET_CRITICAL_THRESHOLD: float = 0.9  # 90% of budget used

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
