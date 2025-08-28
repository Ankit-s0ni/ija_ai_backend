import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, ConfigDict


def _get_list_from_env(key: str):
    val = os.getenv(key, "")
    return [v.strip() for v in val.split(",") if v]


load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

class Settings(BaseSettings):
    PROJECT_NAME: str = "Intelligent Job Assistant"
    PROJECT_VERSION: str = "0.1.0"

    # CORS origins - simple string that we'll split manually
    BACKEND_CORS_ORIGINS: str = ""

    # MongoDB
    MONGODB_URI: str
    MONGODB_DATABASE: str

    # JWT
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # Google OAuth2
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str

    # Google Gemini API
    GEMINI_API_KEY: str
    # LLM model name (e.g., gpt-4, gemini-2.5-flash)
    LLM_MODEL: str = "gemini-2.5-flash"

    # ignore extra environment variables
    model_config = ConfigDict(extra="ignore")


settings = Settings()
