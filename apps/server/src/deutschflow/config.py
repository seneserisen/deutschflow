from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DEUTSCHFLOW_", case_sensitive=False)

    host: str = "127.0.0.1"
    port: int = 43131
    data_dir: Path = Path.home() / ".deutschflow"
    database_url: str | None = None
    provider: str = "argos"
    max_selection_length: int = 500
    max_context_length: int = 2000
    max_body_bytes: int = 1_000_000
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    @property
    def db_url(self) -> str:
        return self.database_url or f"sqlite:///{(self.data_dir / 'deutschflow.db').as_posix()}"


settings = Settings()
