from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://civiceye:civiceye123@localhost/civiceye"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Mapbox
    MAPBOX_TOKEN: Optional[str] = None
    
    # Satellite Data
    SENTINEL_CLIENT_ID: Optional[str] = None
    SENTINEL_CLIENT_SECRET: Optional[str] = None
    
    # Data paths
    DATA_DIR: str = "./data"
    SATELLITE_DIR: str = "./data/satellite"
    MODELS_DIR: str = "./data/models"
    CACHE_DIR: str = "./data/cache"
    
    # ML Settings
    CHANGE_DETECTION_MODEL: str = "baseline"
    HUMAN_CLASSIFICATION_MODEL: str = "baseline"
    ACTIVITY_CLASSIFICATION_MODEL: str = "baseline"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
