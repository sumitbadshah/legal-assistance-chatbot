from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://legal_user:legal_pass@db:5432/legal_assistant"

    # Auth
    secret_key: str = "change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24h

    # LLM provider (Google Gemini). Set your real GEMINI_API_KEY in environment / .env
    gemini_api_key: str = ""
    anthropic_api_key: str = ""  # Backward compatibility alias
    llm_model: str = "gemini-2.5-flash"
    llm_max_tokens: int = 1200

    # CORS - comma separated list of allowed origins
    allowed_origins: str = "http://localhost:3000,http://localhost:5173"

    class Config:
        env_file = ".env"

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
