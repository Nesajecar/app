from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Database - SQLite
    DATABASE_URL: str = "sqlite:///./dog_rescue.db"
    
    # JWT Settings
    JWT_SECRET_KEY: str = "your-super-secret-jwt-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # File Storage
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 5242880  # 5MB
    ALLOWED_EXTENSIONS: List[str] = ["jpg", "jpeg", "png"]
    
    # App Settings
    DEBUG: bool = True
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    
    class Config:
        env_file = ".env"

settings = Settings()
