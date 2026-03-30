from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    APP_NAME: str = "AI Tech Intelligence Platform"
    GEMINI_API_KEY: str
    GITHUB_TOKEN: str
    NEWSAPI_KEY: str
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_CHAT_ID: str
    MONGODB_URI: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "ai_intel_db"
    REDIS_URL: str = "redis://localhost:6379/0"

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
