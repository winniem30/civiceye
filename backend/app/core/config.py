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
    
    # Sentinel-2 STAC
    STAC_ENDPOINT: str = "https://earth-search.aws.element84.com/v1"
    SENTINEL_COLLECTION: str = "sentinel-2-l2a"
    
    # Data paths
    DATA_DIR: str = "./data"
    SATELLITE_DIR: str = "./data/satellite"
    RASTER_DIR: str = "./data/rasters"
    MODELS_DIR: str = "./data/models"
    CACHE_DIR: str = "./data/cache"
    
    # Processing settings
    MAX_CLOUD_COVER: float = 20.0
    MAX_DOWNLOAD_SIZE_MB: int = 500
    PROCESSING_TIMEOUT_SECONDS: int = 300
    
    # ML Settings
    CHANGE_DETECTION_MODEL: str = "baseline"
    HUMAN_CLASSIFICATION_MODEL: str = "baseline"
    ACTIVITY_CLASSIFICATION_MODEL: str = "baseline"
    
    # CORS
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
