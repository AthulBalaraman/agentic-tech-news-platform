from pydantic_settings import BaseSettings, SettingsConfigDict
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
    CHROMA_DB_DIR: str = "./chroma_data"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache()
def get_settings():
    return Settings()
