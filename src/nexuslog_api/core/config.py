from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "NexusLog API"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "sqlite:///./nexuslog.db"  # 默认使用 SQLite，后续可以从 .env 文件读取

    # JWT Settings
    # SECRET_KEY: str = "a_very_secret_key_that_should_be_changed" # 请务必修改此密钥并从环境变量读取
    SECRET_KEY: str = os.getenv("SECRET_KEY", "a_very_secret_key_that_should_be_changed") # 请务必修改此密钥并从环境变量读取
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Uvicorn settings (仅在 main.py 中直接运行时使用)
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    APP_RELOAD: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        case_sensitive=True,
        extra='ignore'  # 允许额外的字段
    )

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()