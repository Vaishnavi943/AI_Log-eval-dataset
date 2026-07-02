from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql://postgres:postgres@localhost:5432/eval_builder"
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    # comma-separated list, e.g. "http://localhost:5173,https://your-app.vercel.app"
    cors_origins_raw: str = Field(default="http://localhost:5173", alias="CORS_ORIGINS")

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins_raw.split(",") if origin.strip()]


settings = Settings()
