import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./tearide.db")
    
    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # CORS
    ALLOWED_ORIGINS: list = os.getenv("ALLOWED_ORIGINS", "*").split(",")

settings = Settings()
