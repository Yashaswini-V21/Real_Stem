"""Configuration settings for RealSTEM backend"""
from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    """Application configuration with environment variables"""
    
    # Application Settings
    APP_NAME: str = "RealSTEM"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"  # development, staging, production
    DEBUG: bool = True
    
    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    API_PREFIX: str = "/api"
    
    # Database Settings
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/realstem"
    DATABASE_ECHO: bool = False
    SQLALCHEMY_POOL_SIZE: int = 20
    SQLALCHEMY_MAX_OVERFLOW: int = 40
    SQLALCHEMY_POOL_TIMEOUT: int = 30
    SQLALCHEMY_POOL_RECYCLE: int = 3600
    
    # Redis & Cache Settings
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL: int = 3600  # 1 hour
    CACHE_ENABLED: bool = True
    
    # Security Settings
    SECRET_KEY: str = "your-secret-key-change-in-production-immediately"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS Settings
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:3000",
    ]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    
    # AI & LLM API Keys
    CLAUDE_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    HUGGING_FACE_API_KEY: str = ""
    
    # News API Keys
    NEWSAPI_KEY: str = ""
    REDDIT_CLIENT_ID: str = ""
    REDDIT_CLIENT_SECRET: str = ""
    REDDIT_USER_AGENT: str = "RealSTEM/1.0 by YourUsername"
    
    # Media & Translation API Keys
    GOOGLE_CLOUD_TTS_API_KEY: str = ""
    GOOGLE_CLOUD_PROJECT_ID: str = ""
    DEEPL_API_KEY: str = ""
    DEEPL_API_URL: str = "https://api-free.deepl.com/v1"
    
    # Celery Settings
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    CELERY_TIMEZONE: str = "UTC"
    CELERY_TASK_TRACK_STARTED: bool = True
    CELERY_TASK_TIME_LIMIT: int = 30 * 60  # 30 minutes
    
    # Email Settings
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SENDER_EMAIL: str = "noreply@realstem.edu"
    SENDER_NAME: str = "RealSTEM"
    
    # Logging Settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: str = "logs/realstem.log"
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Feature Flags
    ENABLE_VIDEO_GENERATION: bool = True
    ENABLE_SIMULATIONS: bool = True
    ENABLE_GLOBAL_CHALLENGES: bool = True
    ENABLE_REAL_TIME_COLLABORATION: bool = True
    ENABLE_ML_RECOMMENDATIONS: bool = True
    ENABLE_MULTI_LANGUAGE: bool = True
    ENABLE_NEWS_AGGREGATION: bool = True
    ENABLE_CAREER_MATCHING: bool = True
    ENABLE_ANALYTICS: bool = True
    
    # Model Settings
    MAX_LESSON_CONTENT_LENGTH: int = 100000  # characters
    MAX_NEWS_DESCRIPTION_LENGTH: int = 5000
    MAX_VIDEO_DURATION_MINUTES: int = 120
    
    # S3/Cloud Storage Settings (if needed)
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    AWS_S3_BUCKET: str = "realstem-content"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        validate_default = True
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.ENVIRONMENT.lower() == "development"
    
    def get_database_url(self) -> str:
        """Get database URL with echo setting"""
        return self.DATABASE_URL


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()
