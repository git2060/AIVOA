import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Load .env
load_dotenv()

class Settings(BaseSettings):
    """Configuration settings for the FastAPI application."""

    PROJECT_NAME: str = "AI-HCP-CRM-API"
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:admin@localhost:5432/crm_db"
    )

    # GROQ credentials
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

    # LangGraph/Checkpoint
    LANGGRAPH_CHECKPOINTER_URL: str = os.getenv(
        "LANGGRAPH_CHECKPOINTER_URL",
        "sqlite:///./langgraph_state.db"
    )

    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]

    # Mandatory for pydantic v2
    model_config = SettingsConfigDict(case_sensitive=True)


# Global settings object
settings = Settings()
