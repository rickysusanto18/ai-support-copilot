from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "AI Support Copilot"
    app_version: str = "0.1.0"

    database_url: str = (
        "postgresql+psycopg://"
        "copilot:copilot@localhost:5432/copilot"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

settings = Settings()